from __future__ import annotations

from typing import Optional

try:
    from starlette.middleware.base import BaseHTTPMiddleware
except Exception:  # pragma: no cover
    BaseHTTPMiddleware = object  # type: ignore


class HanditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, agent: str = "fastapi") -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._agent = agent

    async def dispatch(self, request, call_next):  # type: ignore[no-untyped-def]
        # Import here to avoid import cycles if native extension isn't present at import time
        from handit_ai import session

        attrs = {"path": str(getattr(request, "url", "")), "method": getattr(request, "method", "")}  # type: ignore[dict-item]
        with session(tag=self._agent, attrs=attrs):
            return await call_next(request)


def use_fastapi(app, agent: Optional[str] = None) -> None:  # type: ignore[no-untyped-def]
    agent = agent or "fastapi"
    app.add_middleware(HanditMiddleware, agent=agent)


