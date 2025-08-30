from __future__ import annotations

try:
    # Load the native extension built by maturin as handit_core_native
    from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover - not built yet
    _native = None  # type: ignore


def version() -> str:
    return "0.0.1"  # synced with Cargo.toml for now


class handit:
    @staticmethod
    def start(**kwargs):  # placeholder
        return True

    @staticmethod
    def stop():  # placeholder
        return True

    @staticmethod
    def session(*args, **kwargs):  # placeholder
        from contextlib import contextmanager

        @contextmanager
        def _cm():
            yield

        return _cm()

# Minimal public API for manual calls from Python for early testing
if _native is not None:
    start_session = _native.start_session_py
    on_call = _native.on_call_py
    on_return = _native.on_return_py
    on_exception = _native.on_exception_py
else:
    def start_session(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_call(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_return(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")
    def on_exception(*args, **kwargs):  # type: ignore
        raise RuntimeError("handit_core native extension not built")


