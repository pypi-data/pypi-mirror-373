from copy import deepcopy
import gc                                                                   
from loguru import logger

from dtx_attacks.base.gates import require_deps, torch
from dtx_attacks.base.gates import AutoModelForCausalLM, mp

from dtx_attacks.models.feedback.gradients import GradientFeedback
from dtx_attacks.models.feedback.logits import LogitsFeedback
from dtx_attacks.models.feedback.loss import LossFeedback

from dtx_attacks.evaluation.scorers.pattern import PatternScorer


class PrefixPromptManager:
    def __init__(self, *, tokenizer, conv_template, instruction, target, adv_string):
        r"""
        :param ~str instruction: the harmful query.
        :param ~str target: the target response for the query.
        :param ~str adv_string: the jailbreak prompt.
        """
        self.tokenizer = tokenizer
        self.conv_template = conv_template
        self.instruction = instruction
        self.target = target
        self.adv_string = adv_string

        # slices filled by _update_ids / get_prompt
        self._user_role_slice = slice(0, 0)
        self._goal_slice = slice(0, 0)
        self._control_slice = slice(0, 0)
        self._assistant_role_slice = slice(0, 0)
        self._target_slice = slice(0, 0)
        self._loss_slice = slice(0, 0)

        self.input_ids = None  # populated by get_input_ids/_update_ids

    def get_real_end(self, toks):
        # find last eos within 4 tokens from the end; otherwise end of seq
        if not toks:
            return 0
        end = len(toks)
        for k in range(len(toks) - 1, max(-1, len(toks) - 5), -1):
            if toks[k] == self.tokenizer.eos_token_id:
                return k
        return end

    def fix_ids(self, ids):
        # remove extra leading BOS and trailing EOS runs
        new_start = 0
        new_end = len(ids)
        for i in range(1, len(ids)):
            if ids[i] == self.tokenizer.bos_token_id:
                new_start = i
            else:
                break
        for i in range(len(ids) - 1, -1, -1):
            if ids[i] == self.tokenizer.eos_token_id:
                new_end = i + 1
            else:
                break
        return ids[new_start:new_end]

    @require_deps("torch", "transformers")
    def get_prompt(self, adv_string=None):
        if adv_string is not None:
            self.adv_string = adv_string

        self.conv_template.append_message(
            self.conv_template.roles[0], f"{self.adv_string} {self.instruction}"
        )
        self.conv_template.append_message(self.conv_template.roles[1], f"{self.target}")
        prompt = self.conv_template.get_prompt()

        encoding = self.tokenizer(prompt)
        _ = encoding.input_ids  # kept for parity with original flow

        if self.conv_template.name in ["llama-2", "mistral"]:  # use_fast=True for mistral
            self.conv_template.messages = []

            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._user_role_slice = slice(None, len(toks))

            self.conv_template.append_message(self.conv_template.roles[0], self.adv_string)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._control_slice = slice(self._user_role_slice.stop, max(self._user_role_slice.stop, self.get_real_end(toks)))

            separator = " " if self.instruction else ""
            self.conv_template.update_last_message(f"{self.adv_string}{separator}{self.instruction}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._goal_slice = slice(self._control_slice.stop, self.get_real_end(toks))

            self.conv_template.append_message(self.conv_template.roles[1], None)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._assistant_role_slice = slice(self._control_slice.stop, len(toks))

            self.conv_template.update_last_message(f"{self.target}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)

            target_end_pos = self.get_real_end(toks)
            self._target_slice = slice(self._assistant_role_slice.stop, target_end_pos)
            self._loss_slice = slice(self._assistant_role_slice.stop - 1, target_end_pos - 1)

        else:
            self.conv_template.messages = []

            self.conv_template.append_message(self.conv_template.roles[0], None)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._user_role_slice = slice(None, len(toks))

            self.conv_template.update_last_message(f"{self.adv_string}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._control_slice = slice(self._user_role_slice.stop, max(self._user_role_slice.stop, self.get_real_end(toks)))

            separator = " " if self.instruction else ""
            self.conv_template.update_last_message(f"{self.adv_string}{separator}{self.instruction}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._goal_slice = slice(self._control_slice.stop, self.get_real_end(toks))

            self.conv_template.append_message(self.conv_template.roles[1], None)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._assistant_role_slice = slice(self._control_slice.stop, len(toks))

            self.conv_template.update_last_message(f"{self.target}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)

            target_end_pos = self.get_real_end(toks)
            self._target_slice = slice(self._assistant_role_slice.stop, target_end_pos)
            self._loss_slice = slice(self._assistant_role_slice.stop - 1, target_end_pos - 1)

        self.conv_template.messages = []
        return prompt

    @require_deps("torch", "transformers")
    def get_input_ids(self, adv_string=None):
        prompt = self.get_prompt(adv_string=adv_string)
        toks = self.fix_ids(self.tokenizer(prompt).input_ids)
        input_ids = torch.tensor(toks[: self._target_slice.stop])
        self.input_ids = input_ids
        return input_ids

    # ---- Chat template helpers (no heavy deps) --------------------------------
    def custom_add_generation_prompt(self, messages):
        TEXT = "FKDJSFJFKJDLJF"
        if len(messages) == 0:
            next_role = "user"
        else:
            next_role = "assistant" if messages[-1]["role"] == "user" else "user"

        prompt = self.tokenizer.apply_chat_template(
            messages + [{"role": next_role, "content": TEXT}],
            tokenize=False,
        )
        idx = prompt.find(TEXT)
        ret = prompt[:idx]
        if ret.endswith(" "):
            ret = ret[:-1]
        return ret

    def custom_apply_chat_template(self, messages, remove_special_end=False):
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        if remove_special_end:
            last_text = messages[-1]["content"]
            idx = prompt.rindex(last_text)
            prompt = prompt[: idx + len(last_text)]
        return prompt

    @require_deps("torch", "transformers")
    def _update_ids(self):
        messages = [
            {"role": "user", "content": f"{self.goal} {self.control}"},
            {"role": "assistant", "content": f"{self.target}"},
        ]
        prompt = self.custom_apply_chat_template(messages, remove_special_end=False)
        encoding = self.tokenizer(prompt)
        toks = self.fix_ids(encoding.input_ids)

        if self.conv_template.name in ["llama-2", "mistral"]:
            self.conv_template.messages = []

            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._user_role_slice = slice(None, len(toks))

            self.conv_template.append_message(self.conv_template.roles[0], self.goal)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._goal_slice = slice(self._user_role_slice.stop, max(self._user_role_slice.stop, self.get_real_end(toks)))

            sep = " " if self.goal and self.control and self.control[0] != " " else ""
            self.conv_template.update_last_message(f"{self.goal}{sep}{self.control}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt().strip()).input_ids)
            self._control_slice = slice(self._goal_slice.stop, self.get_real_end(toks))

            self.conv_template.append_message(self.conv_template.roles[1], None)
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)
            self._assistant_role_slice = slice(self._control_slice.stop, len(toks))

            self.conv_template.update_last_message(f"{self.target}")
            toks = self.fix_ids(self.tokenizer(self.conv_template.get_prompt()).input_ids)

            target_end_pos = self.get_real_end(toks)
            self._target_slice = slice(self._assistant_role_slice.stop, target_end_pos)
            self._loss_slice = slice(self._assistant_role_slice.stop - 1, target_end_pos - 1)

        else:
            _prompt = self.custom_add_generation_prompt([])
            toks = self.fix_ids(self.tokenizer(_prompt).input_ids)
            self._user_role_slice = slice(None, len(toks))

            _prompt = self.custom_apply_chat_template([{"role": "user", "content": self.goal}], remove_special_end=True)
            toks = self.fix_ids(self.tokenizer(_prompt).input_ids)
            self._goal_slice = slice(self._user_role_slice.stop, len(toks))

            sep = " " if self.goal and self.control and self.control[0] != " " else ""
            _prompt = self.custom_apply_chat_template(
                [{"role": "user", "content": f"{self.goal}{sep}{self.control}"}],
                remove_special_end=True,
            )
            toks = self.fix_ids(self.tokenizer(_prompt).input_ids)
            self._control_slice = slice(self._goal_slice.stop, len(toks))

            _prompt = self.custom_add_generation_prompt(
                [{"role": "user", "content": f"{self.goal}{sep}{self.control}"}]
            )
            toks = self.fix_ids(self.tokenizer(_prompt).input_ids)
            self._assistant_role_slice = slice(self._control_slice.stop, len(toks))

            _prompt = self.custom_apply_chat_template(
                [
                    {"role": "user", "content": f"{self.goal}{sep}{self.control}"},
                    {"role": "assistant", "content": self.target},
                ],
                remove_special_end=True,
            )
            toks = self.fix_ids(self.tokenizer(_prompt).input_ids)
            target_end_pos = len(toks)  # no eos removal
            self._target_slice = slice(self._assistant_role_slice.stop, target_end_pos)
            self._loss_slice = slice(self._assistant_role_slice.stop - 1, target_end_pos - 1)

        self.input_ids = torch.tensor(toks[: self._target_slice.stop], device="cpu")
        self.conv_template.messages = []

    @require_deps("torch", "transformers")
    @torch.no_grad()
    def generate(self, model, gen_config=None):
        # avoid mutating a shared generation_config
        if gen_config is None:
            gen_config = deepcopy(model.generation_config)
        if not hasattr(gen_config, "do_sample") or gen_config.do_sample is None:
            gen_config.do_sample = False
        if not hasattr(gen_config, "max_new_tokens") or gen_config.max_new_tokens is None:
            gen_config.max_new_tokens = 32

        if gen_config.max_new_tokens > 32:
            logger.warning("WARNING: max_new_tokens > 32 may cause testing to slow down.")

        input_ids = self.input_ids[: self._assistant_role_slice.stop].to(model.device).unsqueeze(0)
        attn_masks = torch.ones_like(input_ids, device=model.device)
        pad_id = self.tokenizer.pad_token_id
        if pad_id is None:
            pad_id = self.tokenizer.eos_token_id

        output_ids = model.generate(
            input_ids,
            attention_mask=attn_masks,
            generation_config=gen_config,
            pad_token_id=pad_id,
        )[0]

        return output_ids[self._assistant_role_slice.stop :]

    @require_deps("torch", "transformers")
    def generate_str(self, model, gen_config=None):
        return self.tokenizer.decode(self.generate(model, gen_config))

    @require_deps("torch", "transformers")
    def test(self, model, gen_config=None):
        if gen_config is None:
            gen_config = deepcopy(model.generation_config)
            gen_config.max_new_tokens = 32
            gen_config.do_sample = False

        gen_str = self.generate_str(model, gen_config).strip()
        prefix_ids = self.input_ids[: self._assistant_role_slice.stop]
        input_prompt = self.tokenizer.decode(
            prefix_ids.tolist() if hasattr(prefix_ids, "tolist") else prefix_ids,
            clean_up_tokenization_spaces=False,
        )
        logger.info(f"Input: {input_prompt}\nOutput: {gen_str}")

        jailbroken = PatternScorer().score(query=None, response=gen_str)["score"]
        em = self.target in gen_str
        return jailbroken, int(em)

    @require_deps("torch", "transformers")
    @torch.no_grad()
    def test_loss(self, model):
        logits, ids = self.logits(model, return_ids=True)
        return self.target_loss(logits, ids).mean().item()

    @require_deps("torch", "transformers")
    def grad(self, model):
        return self.gradient_feedbacker.get_grad_of_control_tokens(
            model,
            self.input_ids,
            self._control_slice,
            self._target_slice,
            self._loss_slice,
        )

    @require_deps("torch", "transformers")
    @torch.no_grad()
    def logits(self, model, test_controls=None, return_ids=False):
        if test_controls is None:
            test_controls = self.control_toks
        return self.logits_feedbacker.get_logits_with_control_tokens(
            model=model,
            input_ids=self.input_ids,
            test_controls=test_controls,
            control_slice=self._control_slice,
            tokenizer=self.tokenizer,
            return_ids=return_ids,
        )

    def target_loss(self, logits, ids):
        return self.loss_feedbacker.get_sliced_loss(
            logits=logits, ids=ids, target_slice=self._target_slice
        )

    def control_loss(self, logits, ids):
        return self.loss_feedbacker.get_sliced_loss(
            logits=logits, ids=ids, target_slice=self._control_slice
        )

    # -------- read-only helpers / properties (no deps needed) -----------------
    @property
    def assistant_str(self):
        span = self.input_ids[self._assistant_role_slice]
        return self.tokenizer.decode(
            span.tolist() if hasattr(span, "tolist") else span,
            clean_up_tokenization_spaces=False,
        ).strip()

    @property
    def assistant_toks(self):
        return self.input_ids[self._assistant_role_slice]

    @property
    def goal_str(self):
        span = self.input_ids[self._goal_slice]
        return self.tokenizer.decode(
            span.tolist() if hasattr(span, "tolist") else span,
            clean_up_tokenization_spaces=False,
        ).strip()

    @goal_str.setter
    def goal_str(self, goal):
        self.goal = goal
        self._update_ids()

    @property
    def goal_toks(self):
        return self.input_ids[self._goal_slice]

    @property
    def target_str(self):
        span = self.input_ids[self._target_slice]
        return self.tokenizer.decode(
            span.tolist() if hasattr(span, "tolist") else span,
            clean_up_tokenization_spaces=False,
        ).strip()

    @target_str.setter
    def target_str(self, target):
        self.target = target
        self._update_ids()

    @property
    def target_toks(self):
        return self.input_ids[self._target_slice]

    @property
    def control_str(self):
        span = self.input_ids[self._control_slice]
        return self.tokenizer.decode(
            span.tolist() if hasattr(span, "tolist") else span,
            clean_up_tokenization_spaces=False,
        ).strip()

    @control_str.setter
    def control_str(self, control):
        self.control = control
        self._update_ids()

    @property
    def control_toks(self):
        return self.input_ids[self._control_slice]

    @control_toks.setter
    def control_toks(self, control_toks):
        self.control = self.tokenizer.decode(
            control_toks.tolist() if hasattr(control_toks, "tolist") else control_toks,
            clean_up_tokenization_spaces=False,
        )
        self._update_ids()

    @property
    def prompt(self):
        span = self.input_ids[self._goal_slice.start : self._control_slice.stop]
        return self.tokenizer.decode(
            span.tolist() if hasattr(span, "tolist") else span,
            clean_up_tokenization_spaces=False,
        )

    @property
    def input_toks(self):
        return self.input_ids

    @property
    def input_str(self):
        ids = self.input_ids
        return self.tokenizer.decode(
            ids.tolist() if hasattr(ids, "tolist") else ids,
            clean_up_tokenization_spaces=False,
        )

    @property
    def eval_str(self):
        ids = self.input_ids[: self._assistant_role_slice.stop]
        return (
            self.tokenizer.decode(
                ids.tolist() if hasattr(ids, "tolist") else ids,
                clean_up_tokenization_spaces=False,
            )
            .replace("<s>", "")
            .replace("</s>", "")
        )

    # Initialize these after construction to avoid NameError in original code
    gradient_feedbacker = GradientFeedback()
    logits_feedbacker = LogitsFeedback()
    loss_feedbacker = LossFeedback()


class ModelWorker(object):
    """
    Thin process worker wrapper bound to a single model.
    Has deep integration with GCGAttackPrompt/PrefixPromptManager.
    """

    @require_deps("torch", "transformers")
    def __init__(self, model_path, model_kwargs, tokenizer, conv_template, device):
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype="auto",
                trust_remote_code=True,
                **model_kwargs,
            )
            .to(device)
            .eval()
        )
        self.model.requires_grad_(False)  # disable grads wrt weights
        self.tokenizer = tokenizer
        self.conv_template = conv_template
        self.tasks = mp.JoinableQueue()
        self.results = mp.JoinableQueue()
        self.process = None

    @staticmethod
    @require_deps("torch", "transformers")
    def run(model, tasks, results):
        while True:
            task = tasks.get()
            if task is None:
                break
            ob, fn, args, kwargs = task
            try:
                if fn == "grad":
                    with torch.enable_grad():
                        results.put(ob.grad(*args, **kwargs))
                else:
                    with torch.no_grad():
                        if fn == "logits":
                            results.put(ob.logits(*args, **kwargs))
                        elif fn == "contrast_logits":
                            results.put(ob.contrast_logits(*args, **kwargs))
                        elif fn == "test":
                            results.put(ob.test(*args, **kwargs))
                        elif fn == "test_loss":
                            results.put(ob.test_loss(*args, **kwargs))
                        else:
                            # assume callable passed
                            results.put(fn(*args, **kwargs))
            finally:
                tasks.task_done()

    @require_deps("torch", "transformers")
    def start(self):
        # avoid setting start method at import time
        try:
            mp.set_start_method("spawn", force=False)
        except RuntimeError:
            # already set; ignore
            pass

        self.process = mp.Process(
            target=ModelWorker.run,
            args=(self.model, self.tasks, self.results),
        )
        self.process.start()
        logger.info(f"Started worker {self.process.pid} for model {getattr(self.model, 'name_or_path', '<model>')}")
        return self

    @require_deps("torch", "transformers")
    def stop(self):
        self.tasks.put(None)
        if self.process is not None:
            self.process.join()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()
        return self

    def __call__(self, ob, fn, *args, **kwargs):
        # enqueue a deep copy of the object to isolate process memory
        self.tasks.put((deepcopy(ob), fn, args, kwargs))
        return self
