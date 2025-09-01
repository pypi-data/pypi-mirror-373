from __future__ import annotations
from pyinstrument import Profiler
import logging
import re
from typing import Any, Awaitable, Dict, List, Optional, TypeVar, Union
import mdformat

# --------------------------------------------------------------------------- #
# Helper: profile any awaited coroutine and log the timing with its call‑site #
# --------------------------------------------------------------------------- #
T = TypeVar("T")
logger = logging.getLogger(__name__)


async def profile_async_call(awaitable: Awaitable[T], name: str) -> T:
    """
    Run *awaitable*, timing it with an ad‑hoc Profiler instance,
    and log the profiler output.

    Args:
        awaitable:   The coroutine to time.
        name:        Friendly name to show in the log (e.g. function name).

    Returns:
        The awaited result, typed to whatever the coroutine yields.
    """
    profiler = Profiler()            # noqa: F821  (assumes Profiler is already imported)
    profiler.start()
    result: T = await awaitable
    profiler.stop()

    logger.debug(
        "⏱️  Profiled %s\n%s",
        name,
        profiler.output_text(unicode=True, color=True),
    )
    return result
