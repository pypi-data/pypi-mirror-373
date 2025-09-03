import threading
from collections.abc import Callable
from typing import Any, TypeVar

import wx

T = TypeVar("T")


def schedule_task(
    task: Callable[..., T],
    error: Callable[[Exception], None],
    resume: Callable[[T], None],
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> None:
    def run() -> None:
        try:
            result = task(*args, **kwargs)
            wx.CallAfter(resume, result)
        except Exception as ex:  # noqa: BLE001
            wx.CallAfter(error, ex)

    threading.Thread(target=run).start()
