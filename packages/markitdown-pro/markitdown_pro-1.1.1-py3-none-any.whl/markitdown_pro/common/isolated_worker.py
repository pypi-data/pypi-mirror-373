import multiprocessing as mp
import traceback
from queue import Empty
from typing import Any, Callable, Dict, Tuple

from .logger import logger


def _child_entry(
    func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any], q: mp.Queue
) -> None:
    try:
        res = func(*args, **kwargs)
        q.put(("ok", res))
    except Exception:
        q.put(("err", traceback.format_exc()))


def run_in_process_with_timeout(
    func: Callable[..., Any], *args: Any, timeout_seconds: float, **kwargs: Any
) -> Any:
    """
    Run a blocking function in a child process with a hard timeout.
    Reads from the result queue first to avoid deadlocks on large payloads.
    On timeout, terminates the child and raises TimeoutError.
    """
    ctx = mp.get_context("spawn")
    q: mp.Queue = ctx.Queue(maxsize=1)
    p = ctx.Process(target=_child_entry, args=(func, args, kwargs, q), daemon=True)
    p.start()
    try:
        status, payload = q.get(timeout=timeout_seconds)  # <-- read first; child won't block on put
    except Empty:
        if p.is_alive():
            p.terminate()
            p.join(5)
            logger.error(f"Child process {func.__name__} timed out after {timeout_seconds} seconds")
        raise TimeoutError(f"Operation exceeded {timeout_seconds} seconds and was terminated.")
    else:
        # We got a result; make a best-effort join and return/raise accordingly
        p.join(1)
        if status == "ok":
            return payload
        raise RuntimeError(f"Child error:\n{payload}")
    finally:
        try:
            if p.is_alive():
                p.terminate()
                p.join(1)
        except Exception:
            pass
