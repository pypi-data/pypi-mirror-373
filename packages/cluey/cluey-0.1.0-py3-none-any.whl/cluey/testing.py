from typing import IO, Any, Mapping, Optional, Sequence, Union
from click.testing import CliRunner as ClickCliRunner
from click.testing import Result

from .cli import ClueyTyper


class CliRunner(ClickCliRunner):
    def invoke(  # type: ignore[override]
        self,
        app: ClueyTyper,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[bytes, str, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result:
        # Ensure stable, no-color environment so Rich/Typer don't add styling
        default_env = {"NO_COLOR": "1", "TERM": "dumb", "COLUMNS": "120"}
        merged_env = {**default_env, **(env or {})}

        use_cli = app.getcommand()
        result: Result = super().invoke(
            use_cli,
            args=args,
            input=input,
            env=merged_env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )

        return result
