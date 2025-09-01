"""
thread_watch.py – drop-in helper to log every Thread that is created.

• Counts live threads in real time
• Records the file/line that called Thread(...)
• Survives 3rd-party libs because it replaces threading.Thread globally
"""

import atexit
import logging
import signal
import sys

# ─── thread_watch.py ─────────────────────────────────────────────────────
import threading
import traceback
import weakref

# Public, process-wide registry ───────────────────────────────────────────
active_threads: "weakref.WeakSet[threading.Thread]" = weakref.WeakSet()
_callsites: "weakref.WeakKeyDictionary[threading.Thread, tuple[str, list[str]]]" = weakref.WeakKeyDictionary()
_lock = threading.Lock()

# Original methods we patch around
_orig_init = threading.Thread.__init__
_orig_start = threading.Thread.start


logger = logging.getLogger(__name__)


def _init(self, *a, **kw):
    _orig_init(self, *a, **kw)
    stack = traceback.format_stack(limit=6)[:-2]
    _callsites[self] = (self.name, stack)


def _start(self, *a, **kw):
    with _lock:
        active_threads.add(self)  # add thread to registry
    logger.info("[+THREAD] %s  total=%d", self.name, len(active_threads))
    return _orig_start(self, *a, **kw)


def _run_wrapper(orig_run):
    def wrapped(self, *a, **kw):
        try:
            return orig_run(self, *a, **kw)
        finally:
            with _lock:
                active_threads.discard(self)
            logger.info("[-THREAD] %s  total=%d", self.name, len(active_threads))

    return wrapped


threading_patched = False


def patch_threading():
    """Monkey patch threading to register threads and dump on exit"""
    global threading_patched
    if threading_patched:
        return
    threading_patched = True
    threading.Thread.__init__ = _init
    threading.Thread.start = _start
    threading.Thread.run = _run_wrapper(threading.Thread.run)


# ─────────── public utility helpers ──────────────────────────────────────
def live_threads() -> list[threading.Thread]:
    """Return a *snapshot* list of threads still alive (excludes current)."""
    with _lock:
        return [t for t in active_threads if t.is_alive() and t is not threading.current_thread()]


def join_all(timeout: float | None = None) -> None:
    """Block until every registered thread finishes."""
    for t in live_threads():
        t.join(timeout)


def dump_stacks(level=logging.WARNING) -> None:
    for t in live_threads():
        name, stack = _callsites.get(t, ("<?>", []))
        logger.log(level, "THREAD STILL LIVE: %s (ident=%s)\n%s", name, t.ident, "".join(stack))


# Keep the atexit dump as a last resort
@atexit.register
def _atexit():
    if live_threads():
        logger.warning("Process exiting with %d worker thread(s) alive!", len(live_threads()))
        dump_stacks()
