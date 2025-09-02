import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn

from ingenious.utils.log_levels import LogLevel


class IActionCallable(ABC):
    @abstractmethod
    async def __call__(
        self, progress: "ProgressConsoleWrapper", task_id: TaskID, **kwargs: Any
    ) -> None:
        pass


class ProgressConsoleWrapper:
    def __init__(self, progress: Progress, log_level: int) -> None:
        self.progress: Progress = progress
        self.log_level: int = log_level
        self._completed_items: int = 0
        self._failed_items: int = 0

    def print(
        self, message: str, level: int = LogLevel.INFO, *args: Any, **kwargs: Any
    ) -> None:
        if level >= self.log_level:
            # Check if style is in args or kwargs
            style: Optional[str] = kwargs.get("style", None)
            if style is None:
                # get the string representation of the level
                style = LogLevel.to_string(level).lower()
            # Add the style to the kwargs
            kwargs["style"] = style
            self.progress.console.print(message, *args, **kwargs)

    @property
    def completed_items(self) -> int:
        return self._completed_items

    @completed_items.setter
    def completed_items(self, value: int) -> None:
        self._completed_items = value

    @property
    def failed_items(self) -> int:
        return self._failed_items

    @failed_items.setter
    def failed_items(self, value: int) -> None:
        self._failed_items = value

    def __getattr__(self, attr: str) -> Any:
        # For all other attributes, return the original Progress object's attributes
        return getattr(self.progress, attr)


class stage_executor:
    def __init__(self, log_level: int, console: Console) -> None:
        self.log_level: int = log_level
        self.console: Console = console

    async def perform_stage(
        self,
        option: bool = True,
        action_callables: Optional[List[IActionCallable]] = None,
        stage_name: str = "Stage - No Name Provided",
        **kwargs: Any,
    ) -> None:
        """
        Perform a stage with the given action callables.
        :param option: A boolean value to determine if the stage should be executed.
        :param action_callables: A list of callables to execute.These callables should implement the ActionCallable interface.
        :param stage_name: The name of the stage.
        :param kwargs: Additional keyword arguments to pass to the action callables.
        """
        if action_callables is None:
            action_callables = []

        with Progress(
            SpinnerColumn(
                spinner_name="dots", style="progress.spinner", finished_text="📦"
            ),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            console=self.console,
        ) as progress:
            stage_status: str = "Initiated  "

            # progress.console.print(Panel(f"Stage: {stage_name}"))
            ptid: TaskID = progress.add_task(
                description=f"[{stage_status}] Stage: {stage_name}"
            )
            # Wrap the Progress object
            wrapped_progress: ProgressConsoleWrapper = ProgressConsoleWrapper(
                progress, self.log_level
            )

            start: float = time.time()
            if option:
                stage_status = "Running  🏃‍♂️"
                progress.update(
                    task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}"
                )
                for action_callable in action_callables:
                    await action_callable.__call__(
                        progress=wrapped_progress, task_id=ptid, **kwargs
                    )
                stage_status = "Completed ✅ "
                progress.update(
                    task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}"
                )
            else:
                stage_status = "Skipped  -- "
                progress.update(
                    task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}"
                )
            time.sleep(1)  # Simulate some delay
            runtime: float = time.time() - start
            milliseconds: int = int((runtime % 1) * 1000)
            runtime_str: str = (
                time.strftime("%H:%M:%S", time.gmtime(runtime)) + f".{milliseconds:03d}"
            )
            progress.update(
                task_id=ptid,
                description=f"[{stage_status}] Stage: {stage_name}[info] | Runtime: {runtime_str}[/info]",
                total=1,
                completed=1,
            )
