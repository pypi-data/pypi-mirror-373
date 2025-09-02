from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from handit_core import configure as _configure
from handit_core import entrypoint as _entrypoint
from handit_core import session as session

# Re-export FastAPI helpers for convenience
try:  # pragma: no cover
    from .fastapi import HanditMiddleware, use_fastapi  # type: ignore
except Exception:  # pragma: no cover
    HanditMiddleware = None  # type: ignore
    def use_fastapi(*args, **kwargs):  # type: ignore
        raise RuntimeError("fastapi is not installed; `pip install fastapi` to use handit_ai.use_fastapi")


def configure(**kwargs: Any) -> None:
    """Configure Handit (e.g., HANDIT_ENDPOINT, HANDIT_API_KEY, etc.)."""
    _configure(**kwargs)


def tracing(agent: str, capture: Optional[str] = None, attrs: Optional[Dict[str, str]] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to trace a function with a clear agent name.


         
    Works seamlessly with FastAPI and other frameworks.

    Example with simple FastAPI endpoints:
        @app.post("/process_langgraph", response_model=LGProcessResponse)
        @tracing(agent="langgraph_processing")
        async def process_langgraph(request: LGProcessRequest):
            # Your code here
            pass
            
        # Or in reverse order:
        @tracing(agent="langgraph_processing")
        @app.post("/process_langgraph", response_model=LGProcessResponse)
        async def process_langgraph(request: LGProcessRequest):
            # Your code here
            pass

    For complex FastAPI endpoints with UploadFile/Form, use session context:
        @app.post("/complex", response_model=Response)
        async def complex_endpoint(
            image: UploadFile = File(...),
            currency: str = Form(None)
        ):
            with session(tag="complex_processing"):
                # Your code here - all HTTP calls traced
                return Response(...)

    Regular function example:
        @tracing(agent="checkout")
        def handle(req):
            # Your code here
            pass
    
    Args:
        agent: A clear name for the traced function/endpoint
        capture: Optional capture mode (defaults to None)
        attrs: Optional attributes to attach to the session
    """
    return _entrypoint(tag=agent, capture=capture, attrs=attrs)



# Friendly aliases
trace = tracing

def enable_langchain_tracing():
    """
    Enable automatic LangChain ainvoke tracing
    
    Usage:
        from handit_ai import enable_langchain_tracing
        enable_langchain_tracing()
        
        # Now all ChatOpenAI.ainvoke calls will be traced automatically
    """
    import time
    import json
    
    # Patch ChatOpenAI
    try:
        from langchain_openai import ChatOpenAI
        
        if hasattr(ChatOpenAI, '_handit_patched'):
            return
        
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced ChatOpenAI.ainvoke"""
            
            # Check for active session
            try:
                import handit_core.handit_core_native as native
                session_id = native.get_active_session_id_py()
                if not session_id:
                    return await original_ainvoke(self, input, config, **kwargs)
            except:
                return await original_ainvoke(self, input, config, **kwargs)
            
            # Extract model info
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'gpt-3.5-turbo'))
            t0_ns = time.time_ns()
            
            # Emit call event
            try:
                input_str = str(input)[:300] if input else ""
                args_preview = {"model": model_name, "input": input_str}
                native.on_call_with_args_py(session_id, "ChatOpenAI.ainvoke", "langchain_openai", "<langchain>", 1, t0_ns, json.dumps(args_preview))
            except:
                pass
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                
                # Emit return event
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    response_content = result.content[:500] if hasattr(result, 'content') and result.content else str(result)[:500]
                    return_preview = {"return": response_content}
                    native.on_return_with_preview_py(session_id, "ChatOpenAI.ainvoke", t1_ns, dt_ns, json.dumps(return_preview))
                except:
                    pass
                
                return result
            except Exception as error:
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    error_preview = {"return": f"Error: {str(error)[:200]}"}
                    native.on_return_with_preview_py(session_id, "ChatOpenAI.ainvoke", t1_ns, dt_ns, json.dumps(error_preview))
                except:
                    pass
                raise
        
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
    except ImportError:
        pass
    except Exception as e:
        pass

