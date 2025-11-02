import typing

import argparse

CmdResult = typing.TypedDict(
    "CmdResult",
    {
        "exit_code": int,
        "results": typing.Any,
        "additional_results": typing.Any | None,
    },
)

HandlerCmdType = typing.Callable[[argparse.Namespace], CmdResult]
