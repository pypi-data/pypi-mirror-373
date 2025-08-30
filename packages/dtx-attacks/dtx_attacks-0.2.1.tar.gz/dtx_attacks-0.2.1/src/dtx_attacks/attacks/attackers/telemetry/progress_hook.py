from typing import Any
from abc import ABC, abstractmethod
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from typing import List, Dict
import time

from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn, TimeElapsedColumn
from rich.text import Text
from rich import box



class BaseAttackProgressHook(ABC):
    """
    Abstract base hook for capturing progress from various attack techniques
    (PAIR, TAP, others). Defines a common interface with Behavior/Strategy/Turn
    lifecycle methods plus technique-specific structure and event hooks.

    Subclasses must implement all abstract methods. A typical implementation
    might log events, record them into JSON, or update a live UI.
    """

    # ---------------------
    # Totals (common)
    # ---------------------
    @abstractmethod
    def on_total_behaviors(self, total_behaviors: int) -> None:
        """Called once to report the total number of behaviors to run."""
        ...

    @abstractmethod
    def on_total_strategies(self, total_strategies: int) -> None:
        """Called once to report the total number of strategies."""
        ...

    @abstractmethod
    def on_total_turns(self, total_turns: int) -> None:
        """Called once to report the total number of turns (per strategy or overall)."""
        ...

    # ---------------------
    # Behavior lifecycle
    # ---------------------
    @abstractmethod
    def on_behavior_start(self, behavior_number: int, behavior_idx: int, total_behaviors: int) -> None:
        """Called at the start of a behavior run."""
        ...

    @abstractmethod
    def on_behavior_end(self, behavior_result: Any, behavior_idx: int, total_behaviors: int) -> None:
        """Called at the end of a behavior run with its result object."""
        ...

    # ---------------------
    # Strategy lifecycle
    # ---------------------
    @abstractmethod
    def on_strategy_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        """Called at the start of a strategy within a behavior."""
        ...

    @abstractmethod
    def on_strategy_end(
        self,
        strategy_result: Any,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        """Called at the end of a strategy with its result object."""
        ...

    @abstractmethod
    def on_strategy_end_summary(self, stats: Any) -> None:
        """Called with aggregated statistics at the end of a strategy."""
        ...

    # ---------------------
    # Turn lifecycle
    # ---------------------
    @abstractmethod
    def on_turn_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        global_turn_idx: int,
        total_turns: int,
    ) -> None:
        """Called at the start of an individual turn within a strategy."""
        ...

    @abstractmethod
    def on_turn_end(self, turn_result: Any, global_turn_idx: int, total_turns: int) -> None:
        """Called at the end of an individual turn with its result object."""
        ...

    # ---------------------
    # Plan revisions
    # ---------------------
    @abstractmethod
    def on_plan_revised(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        new_plan: Any,
    ) -> None:
        """Called if the plan for a strategy/turn is revised dynamically."""
        ...

    # ---------------------
    # Success & best tracking
    # ---------------------
    @abstractmethod
    def on_success(self, depth: int, score: float, prompt: str) -> None:
        """Called when a success threshold is reached and early stopping is triggered."""
        ...

    @abstractmethod
    def on_new_global_best(
        self,
        technique: str,
        score: float,
        prev_best: float,
        candidate: dict[str, Any],
    ) -> None:
        """Called when a new global best candidate surpasses the previous best score."""
        ...

    @abstractmethod
    def on_best_score_update(
        self,
        technique: str,
        score: float,
        candidate: dict[str, Any],
    ) -> None:
        """
        Called on every iteration (or turn/strategy) to report the current best
        candidate, even if it hasn't surpassed the previous best.
        """
        ...

    # ---------------------
    # Technique-agnostic structure progress
    # ---------------------
    @abstractmethod
    def on_structure_progress(self, technique: str, structure_type: str, data: dict[str, Any]) -> None:
        """
        Called to report structured progress updates that are technique-specific.

        Examples:
          TAP   → structure_type="depth", data={"depth": 3, "frontier_size": 12}
          PAIR  → structure_type="stream", data={"stream_id": 2, "score": 7.5}
        """
        ...

    # ---------------------
    # Errors
    # ---------------------
    @abstractmethod
    def on_behavior_error(self, exception: Exception, friendly_message: str, behavior_number: int) -> None:
        """Called when an error occurs inside a behavior."""
        ...

    @abstractmethod
    def on_strategy_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
    ) -> None:
        """Called when an error occurs inside a strategy."""
        ...

    @abstractmethod
    def on_turn_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
    ) -> None:
        """Called when an error occurs inside a turn."""
        ...


class LoggingAttackProgressHook(BaseAttackProgressHook):
    """
    A simple concrete implementation of BaseAttackProgressHook
    that just logs progress events with loguru.
    """

    # ---------------------
    # Totals
    # ---------------------
    def on_total_behaviors(self, total_behaviors: int) -> None:
        logger.info(f"[Totals] Behaviors: {total_behaviors}")

    def on_total_strategies(self, total_strategies: int) -> None:
        logger.info(f"[Totals] Strategies: {total_strategies}")

    def on_total_turns(self, total_turns: int) -> None:
        logger.info(f"[Totals] Turns: {total_turns}")

    # ---------------------
    # Behavior lifecycle
    # ---------------------
    def on_behavior_start(self, behavior_number: int, behavior_idx: int, total_behaviors: int) -> None:
        logger.info(f"[Behavior {behavior_number}/{total_behaviors}] START")

    def on_behavior_end(self, behavior_result: Any, behavior_idx: int, total_behaviors: int) -> None:
        success = getattr(behavior_result, "success", None)
        score = getattr(behavior_result, "score", None)
        logger.info(f"[Behavior {behavior_idx}/{total_behaviors}] END | Success={success} | Score={score}")

    # ---------------------
    # Strategy lifecycle
    # ---------------------
    def on_strategy_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        logger.info(f"  [Strategy {strategy_idx}/{total_strategies}] START (global {global_strategy_idx})")

    def on_strategy_end(
        self,
        strategy_result: Any,
        global_strategy_idx: int,
        total_strategies: int,
    ) -> None:
        score = getattr(strategy_result, "score", None)
        logger.info(f"  [Strategy {global_strategy_idx}/{total_strategies}] END | Score={score}")

    def on_strategy_end_summary(self, stats: Any) -> None:
        logger.info(f"  [Strategy Summary] {stats}")

    # ---------------------
    # Turn lifecycle
    # ---------------------
    def on_turn_start(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        global_turn_idx: int,
        total_turns: int,
    ) -> None:
        logger.info(f"    [Turn {turn_idx}/{total_turns}] START (global {global_turn_idx})")

    def on_turn_end(self, turn_result: Any, global_turn_idx: int, total_turns: int) -> None:
        score = getattr(turn_result, "score", None)
        logger.info(f"    [Turn {global_turn_idx}/{total_turns}] END | Score={score}")

    # ---------------------
    # Plan revisions
    # ---------------------
    def on_plan_revised(
        self,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
        new_plan: Any,
    ) -> None:
        logger.info(f"    [Turn {turn_idx}] Plan revised → {new_plan}")

    # ---------------------
    # Success & best tracking
    # ---------------------
    def on_success(self, depth: int, score: float, prompt: str) -> None:
        logger.info(f"[SUCCESS] Depth={depth} | Score={score:.2f} | Prompt={prompt}")

    def on_new_global_best(
        self,
        technique: str,
        score: float,
        prev_best: float,
        candidate: dict[str, Any],
    ) -> None:
        logger.info(
            f"[{technique}] New Global Best! Score={score:.2f} (prev={prev_best:.2f}) | Candidate={candidate}"
        )

    def on_best_score_update(
        self,
        technique: str,
        score: float,
        candidate: dict[str, Any],
    ) -> None:
        logger.info(f"[{technique}] Best so far → Score={score:.2f} | Candidate={candidate}")

    # ---------------------
    # Structure progress
    # ---------------------
    def on_structure_progress(self, technique: str, structure_type: str, data: dict[str, Any]) -> None:
        logger.info(f"[{technique}] {structure_type} progress: {data}")

    # ---------------------
    # Errors
    # ---------------------
    def on_behavior_error(self, exception: Exception, friendly_message: str, behavior_number: int) -> None:
        logger.error(f"[Behavior {behavior_number}] ERROR: {friendly_message} ({exception})")

    def on_strategy_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
    ) -> None:
        logger.error(f"[Behavior {behavior_number} | Strategy {strategy_idx}] ERROR: {friendly_message} ({exception})")

    def on_turn_error(
        self,
        exception: Exception,
        friendly_message: str,
        behavior_number: int,
        strategy_idx: int,
        turn_idx: int,
    ) -> None:
        logger.error(
            f"[Behavior {behavior_number} | Strategy {strategy_idx} | Turn {turn_idx}] "
            f"ERROR: {friendly_message} ({exception})"
        )




class VisualAttackProgressHook:
    """
    Polished Rich dashboard for attack progress with:
      - Stats, progress bars (Behavior/Strategy/Turn)
      - Best Score bar (0–100%)
      - Best Prompt preview under Progress
      - Best Scores leaderboard
    Keeps the same callback surface as your existing hook.
    """

    TITLE = "Detoxio Attack Runner — Progress"

    def __init__(self):
        self.console = Console()
        # Time
        self._t0: float | None = None

        # State
        self.total_behaviors = 0
        self.total_strategies = 0
        self.total_turns = 0
        self.current_behavior = 0
        self.current_depth = 0         # strategy index
        self.current_turn = 0
        self.best_scores: List[Dict[str, Any]] = []   # [{'score': float, 'prompt': str}, ...]
        self.last_success: Dict[str, Any] | None = None
        self.global_best_score: float = 0.0           # 0..1
        self.global_best_prompt: str = ""

        # Progress bars
        self.behavior_prog = Progress(
            TextColumn("Behavior", style="bold"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn(" "),
            TimeElapsedColumn(),
            expand=True,
        )
        self.strategy_prog = Progress(
            TextColumn("Strategy", style="bold"),
            BarColumn(),
            MofNCompleteColumn(),
            expand=True,
        )
        self.turn_prog = Progress(
            TextColumn("Turn", style="bold"),
            BarColumn(),
            MofNCompleteColumn(),
            expand=True,
        )
        self.best_prog = Progress(
            TextColumn("Best Score", style="bold"),
            BarColumn(),
            MofNCompleteColumn(),                   # shows x/10
            TextColumn("{task.percentage:>5.1f}%"), # optional percent
            expand=True,
        )

        # Tasks
        self._behavior_task = self.behavior_prog.add_task("behavior", total=1, completed=0)
        self._strategy_task = self.strategy_prog.add_task("strategy", total=1, completed=0)
        self._turn_task = self.turn_prog.add_task("turn", total=1, completed=0)
        self._best_task = self.best_prog.add_task("best", total=10, completed=0)

        # Live dashboard
        self.live = Live(self._render_layout(), console=self.console, refresh_per_second=6)

    # ---------- Rendering ----------

    def _header(self) -> Panel:
        elapsed = 0.0 if self._t0 is None else time.time() - self._t0
        title = Text(self.TITLE, style="bold white")
        subtitle = Text.assemble(
            ("  |  ", "dim"),
            (f"Behavior {self.current_behavior}/{self.total_behaviors}", "cyan"),
            ("  •  ", "dim"),
            (f"Strategy {self.current_depth}/{self.total_strategies}", "magenta"),
            ("  •  ", "dim"),
            (f"Turn {self.current_turn}/{self.total_turns}", "yellow"),
            ("  •  ", "dim"),
            (f"Best {self.global_best_score:.2f}/10", "green"),
            ("  •  ", "dim"),
            (f"Elapsed {int(elapsed)}s", "green"),
        )

        return Panel(Group(title, Text(""), subtitle), box=box.ROUNDED, border_style="cyan", padding=(1, 2))

    def _stats_table(self) -> Panel:
        t = Table.grid(padding=(0, 2))
        t.add_column(justify="left", style="bold cyan")
        t.add_column(justify="right", style="white")
        t.add_row("Behaviors", f"{self.total_behaviors}")
        t.add_row("Strategies", f"{self.total_strategies}")
        t.add_row("Turns", f"{self.total_turns}")
        if self.last_success:
            t.add_row("Last Success", f"{self.last_success['score']:.2f}")
        return Panel(t, title="Stats", box=box.ROUNDED, border_style="cyan")

    def _prompt_preview(self, text: str, max_len: int = 160) -> str:
        if not text:
            return "—"
        t = " ".join(text.split())  # collapse whitespace/newlines
        return t if len(t) <= max_len else f"{t[:110]} … {t[-35:]}"

    def _progress_group(self) -> Panel:
        # Update tasks with bounds
        self.behavior_prog.update(self._behavior_task, total=max(1, self.total_behaviors), completed=self.current_behavior)
        self.strategy_prog.update(self._strategy_task, total=max(1, self.total_strategies), completed=self.current_depth)
        self.turn_prog.update(self._turn_task, total=max(1, self.total_turns), completed=self.current_turn)
        self.best_prog.update(self._best_task, completed=float(self.global_best_score))

        best_prompt_panel = Panel(
            self._prompt_preview(self.global_best_prompt),
            title="Best Prompt",
            border_style="green",
        )

        return Panel(
            Group(self.behavior_prog, self.strategy_prog, self.turn_prog, self.best_prog, best_prompt_panel),
            title="Progress",
            box=box.ROUNDED,
            border_style="cyan",
        )

    def _best_table(self) -> Panel:
        table = Table(box=box.ROUNDED, expand=True, header_style="bold green", border_style="green")
        table.add_column("Score", justify="center", width=7)
        table.add_column("Prompt (preview)", overflow="fold")
        if not self.best_scores:
            table.add_row("—", "No successes yet")
        else:
            for b in self.best_scores[:10]:
                prompt = self._prompt_preview((b.get("prompt") or ""))
                table.add_row(f"{b.get('score', 0):.2f}", prompt)
        return Panel(table, title="Best Scores", border_style="green")

    def _render_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=5),
            Layout(name="body"),
            Layout(name="footer", size=1),
        )
        layout["body"].split_row(Layout(name="left"), Layout(name="right"))
        layout["left"].ratio = 1
        layout["right"].ratio = 2

        layout["header"].update(self._header())
        layout["left"].update(self._stats_table())
        layout["right"].update(
            Group(
                self._progress_group(),
                self._best_table(),
            )
        )
        layout["footer"].update(Text("Press Ctrl+C to stop view (runner continues).", style="dim"))
        return layout

    def _refresh(self):
        if self.live.is_started:
            layout = self._render_layout()
            self.live.update(layout)

    # ---------- Lifecycle: same callback names as your current hook ----------

    def on_total_behaviors(self, total_behaviors: int) -> None:
        self.total_behaviors = total_behaviors
        self._refresh()

    def on_total_strategies(self, total_strategies: int) -> None:
        self.total_strategies = total_strategies
        self._refresh()

    def on_total_turns(self, total_turns: int) -> None:
        self.total_turns = total_turns
        self._refresh()

    def on_behavior_start(self, behavior_number: int, behavior_idx: int, total_behaviors: int) -> None:
        if not self.live.is_started:
            self._t0 = time.time()
            self.live.start()
        self.current_behavior = behavior_idx
        self.total_behaviors = total_behaviors
        self._refresh()

    def on_behavior_end(self, behavior_result: Any, behavior_idx: int, total_behaviors: int) -> None:
        self.current_behavior = behavior_idx
        self._refresh()

    def on_strategy_start(self, behavior_number: int, strategy_idx: int,
                          global_strategy_idx: int, total_strategies: int) -> None:
        self.current_depth = strategy_idx
        self.total_strategies = total_strategies
        self._refresh()

    def on_strategy_end(self, strategy_result: Any, global_strategy_idx: int,
                        total_strategies: int) -> None:
        self._refresh()

    def on_strategy_end_summary(self, stats: Any) -> None:
        self._refresh()

    def on_turn_start(self, behavior_number: int, strategy_idx: int,
                      turn_idx: int, global_turn_idx: int, total_turns: int) -> None:
        self.current_turn = turn_idx
        self.total_turns = total_turns
        self._refresh()

    def on_turn_end(self, turn_result: Any, global_turn_idx: int, total_turns: int) -> None:
        self._refresh()

    def on_success(self, depth: int, score: float, prompt: str) -> None:
        self.last_success = {"score": score, "prompt": prompt}
        self.best_scores.insert(0, {"score": score, "prompt": prompt})
        self.best_scores = self.best_scores[:10]
        if score > self.global_best_score:
            self.global_best_score = float(score)      # score is 1..10
            self.global_best_prompt = prompt
        self.console.rule(f"[bold green]SUCCESS at Depth {depth} | Score={score:.2f}")
        self._refresh()

    def on_new_global_best(self, technique: str, score: float, prev_best: float, candidate: Dict[str, Any]) -> None:
        self.best_scores.insert(0, {"score": score, "prompt": candidate.get("prompt", "")})
        self.best_scores = self.best_scores[:10]
        if score > self.global_best_score:
            self.global_best_score = score
            self.global_best_prompt = candidate.get("prompt", "")
        self._refresh()

    def on_best_score_update(self, technique: str, score: float, candidate: Dict[str, Any]) -> None:
        if score > self.global_best_score:
            self.global_best_score = score
            self.global_best_prompt = candidate.get("prompt", self.global_best_prompt)
        self._refresh()

    def on_structure_progress(self, technique: str, structure_type: str, data: Dict[str, Any]) -> None:
        self._refresh()

    def on_behavior_error(self, exception: Exception, friendly_message: str, behavior_number: int) -> None:
        self.console.print(f"[red]Behavior {behavior_number} ERROR: {friendly_message} ({exception})")

    def on_strategy_error(self, exception: Exception, friendly_message: str,
                          behavior_number: int, strategy_idx: int) -> None:
        self.console.print(f"[red]Behavior {behavior_number} | Strategy {strategy_idx} ERROR: {friendly_message} ({exception})")

    def on_turn_error(self, exception: Exception, friendly_message: str,
                      behavior_number: int, strategy_idx: int, turn_idx: int) -> None:
        self.console.print(f"[red]Behavior {behavior_number} | Strategy {strategy_idx} | Turn {turn_idx} ERROR: {friendly_message} ({exception})")

    def on_plan_revised(self, behavior_number: int, strategy_idx: int, turn_idx: int, new_plan: Any) -> None:
        self.console.print(f"[yellow]Plan revised at Turn {turn_idx}: {new_plan}")

    def stop(self) -> None:
        if self.live.is_started:
            self.live.stop()
            self.console.rule("[bold]Run complete")
