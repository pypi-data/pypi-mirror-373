from __future__ import annotations

from typing import List, Optional, Iterator, Dict, Any
import json
import os
import random


SeedList = List[str]
# JSON structure: {"attack": {"Gptfuzzer": [..], ...}, "judge": {...}}
TemplateDict = Dict[str, Dict[str, SeedList]]


class SeedBase:
    def __init__(self, seeds: Optional[SeedList] = None) -> None:
        self.seeds: SeedList = [] if seeds is None else seeds

    def __iter__(self) -> Iterator[str]:
        return iter(self.seeds)

    def new_seeds(self, **kwargs) -> SeedList:
        raise NotImplementedError


class SeedTemplate(SeedBase):
    """
    Unified class:
    - `new_seeds(...)` : original functionality using (prompt_usage, method_list)
    - `get_templates(name, num, template_file)` : supports the simpler "init_templates.json" schema
    - `init_population(data_path)` : loads arbitrary population JSON
    """

    def __init__(self, seeds: Optional[SeedList] = None, rng: Optional[random.Random] = None) -> None:
        super().__init__(seeds)
        # Allow injecting a deterministic RNG (e.g., random.Random(0)) for tests/CI
        self._rng: random.Random = rng or random

    # ---------- Shared helpers ----------
    @staticmethod
    def _resolve_path(default_filename: str, provided: Optional[str]) -> str:
        if provided:
            return provided
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, default_filename)

    @staticmethod
    def _load_json(path: str) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- Original API ----------
    def new_seeds(
        self,
        seeds_num: Optional[int] = None,
        prompt_usage: str = "attack",
        method_list: Optional[List[str]] = None,
        template_file: Optional[str] = None,
    ) -> SeedList:
        """
        Uses a schema like:
        {
          "attack": {
            "Gptfuzzer": [...],
            "DeepInception": [...],
            "ICA": [...],
            "default": [...]
          },
          "judge": { ... }
        }
        """
        self.seeds = []
        if method_list is None:
            method_list = ["default"]

        path = self._resolve_path("seed_template.json", template_file)
        template_dict: TemplateDict = self._load_json(path)

        # Build pool
        try:
            usage_block = template_dict[prompt_usage]
        except KeyError as exc:
            raise AttributeError(f"{path} has no top-level key '{prompt_usage}'") from exc

        template_pool: SeedList = []
        for method in method_list:
            try:
                template_pool.extend(usage_block[method])
            except KeyError as exc:
                raise AttributeError(
                    f"{path} contains no {prompt_usage} prompt template from the method {method}"
                ) from exc

        if seeds_num is None:
            return template_pool

        assert seeds_num > 0, "The seeds_num must be a positive integer."
        assert seeds_num <= len(template_pool), (
            "The number of seeds in the template pool is less than the number being asked for."
        )

        # Use injected RNG for testability
        indices = self._rng.sample(range(len(template_pool)), seeds_num)
        self.seeds = [template_pool[i] for i in indices]
        return self.seeds

    # ---------- Simple "InitTemplates" API ----------
    def get_templates(
        self,
        name: str,
        num: int,
        template_file: Optional[str] = None,
        root_key: str = "attack",
        default_filename: str = "seed_template.json",
    ) -> SeedList:
        """
        Supports files shaped like:
        { "attack": { "<name>": [ "tmpl1", "tmpl2", ... ] } }
        - num = -1 → return all
        """
        path = self._resolve_path(default_filename, template_file)
        data: Dict[str, Dict[str, SeedList]] = self._load_json(path)

        try:
            all_templates = data[root_key][name]
        except KeyError as exc:
            raise AttributeError(f"{path} is missing '{root_key}' or '{name}'") from exc

        if num == -1:
            return list(all_templates)

        if num < 0:
            raise ValueError("num must be -1 (all) or a nonnegative integer.")
        if num > len(all_templates):
            raise AssertionError("Requested num exceeds available templates.")

        return self._rng.sample(all_templates, num)

    # ---------- Population loader ----------
    @staticmethod
    def init_population(data_path: str) -> Any:
        """
        Loads a JSON file that describes a population.
        Shape is user-defined; returns the parsed JSON as-is.
        """
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

if __name__ == "__main__":
    seedtemplate = SeedTemplate()
    new_seeds = seedtemplate.new_seeds(
        seeds_num=3,
        prompt_usage="attack",
        method_list=["Gptfuzzer", "DeepInception", "ICA", "ICA"],
    )
    print(new_seeds)
    print(len(new_seeds))
