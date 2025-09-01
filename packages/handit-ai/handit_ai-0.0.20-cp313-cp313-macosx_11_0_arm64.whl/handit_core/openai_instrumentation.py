"""OpenAI instrumentation to capture high-level API calls."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
    from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
    _native = None  # type: ignore

from . import _active_session_id  # type: ignore

import json, dataclasses, base64
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime

def to_jsonable(x):
    # Handle None first
    if x is None:
        return None
    
    # Built-ins (fast path)
    if isinstance(x, (str, int, float, bool)):
        return x
    
    # Pydantic v2 (OpenAI v1+) - with error handling
    if hasattr(x, "model_dump"):
        try:
            return x.model_dump()
        except Exception:
            # Fallback if model_dump fails
            pass
    
    # Pydantic v1 / common libs
    if hasattr(x, "dict"):
        try:
            return x.dict()
        except Exception:
            pass
    
    # Dataclasses
    if dataclasses.is_dataclass(x):
        try:
            return dataclasses.asdict(x)
        except Exception:
            pass
    
    # Collections
    if isinstance(x, (list, tuple, set, frozenset)):
        try:
            return [to_jsonable(v) for v in x]
        except Exception:
            return [str(v) for v in x]
    
    if isinstance(x, dict):
        try:
            return {str(k): to_jsonable(v) for k, v in x.items()}
        except Exception:
            return {str(k): str(v) for k, v in x.items()}
    
    # Common non-JSON types
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, (UUID, Decimal)):
        return str(x)
    if isinstance(x, (bytes, bytearray)):
        return base64.b64encode(x).decode("utf-8")
    
    # Last resort with error handling
    if hasattr(x, "__dict__"):
        try:
            return {k: to_jsonable(v) for k, v in vars(x).items()}
        except Exception:
            return {"<serialization-error>": str(x)}
    
    # Final fallback
    return str(x)

def to_json_string(obj) -> str:
    return json.dumps(to_jsonable(obj), ensure_ascii=False, separators=(",", ":"))

def patch_openai() -> None:
    """Patch OpenAI to emit custom events for API calls"""
    try:
        import openai
        from openai.resources.chat import completions
    except Exception:
        return
    
    # Prevent double patching
    if getattr(completions.Completions.create, "_handit_patched", False):
        return
    
    orig_create = completions.Completions.create
    
    def wrapped_create(self, **kwargs):  # type: ignore[no-untyped-def]
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        
        # Extract other params for logging (avoid **kwargs conflict)
        other_params = {k: v for k, v in kwargs.items() if k not in ["model", "messages"]}
        params = {
            "model": model,
            "messages": messages,
            **other_params
        }
        # Emit call event
        _native_on = getattr(_native, "on_call_with_args_py", None)
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _native_on is None or _return_on is None:
            return
        sid = _active_session_id.get()
        if not sid or _native is None:
            return 0
        
        func_name = "create"  # Just "create"
        module_name = "openai.resources.chat.completions"
        file_name = "<openai-api>"
        line_no = 1
        t0 = time.time_ns()

        if isinstance(params, dict):
            params_dict = params
        else:
            params_dict = params.to_dict()

        params_json = to_json_string(params_dict)

        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        
        try:
            # Make the actual call
            result = orig_create(self, **kwargs)
            
            # Emit return event
            t1 = time.time_ns()
            dt_ns = t1 - t0
            result_json = to_json_string(result)
            _return_on(sid, func_name, t1, dt_ns, result_json)
            
            return result
            
        except Exception as e:
            raise
    
    setattr(wrapped_create, "_handit_patched", True)
    setattr(wrapped_create, "_handit_orig", orig_create)
    completions.Completions.create = wrapped_create  # type: ignore

def patch_openai_client_for_langchain():
    """Patch LangChain at the right level - when models are actually imported"""
    
    # Strategy: Patch the module import system to catch LangChain models when imported
    import sys
    import importlib.util
    
    # Store original import
    original_import = __builtins__['__import__']
    
    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Custom import that patches LangChain models as they're imported"""
        
        # Call original import first
        module = original_import(name, globals, locals, fromlist, level)
        
        # Check if this is a LangChain model import
        if name == 'langchain_openai' or (fromlist and 'ChatOpenAI' in fromlist):
            try:
                from langchain_openai import ChatOpenAI
                if not hasattr(ChatOpenAI, '_handit_patched'):
                    _patch_chatopenai()
            except:
                pass
        
        if name == 'langchain_anthropic' or (fromlist and 'ChatAnthropic' in fromlist):
            try:
                from langchain_anthropic import ChatAnthropic
                if not hasattr(ChatAnthropic, '_handit_patched'):
                    _patch_chatanthropic()
            except:
                pass
        
        return module
    
    # Apply the import hook
    __builtins__['__import__'] = traced_import

def _patch_chatopenai():
    """Actually patch ChatOpenAI.ainvoke"""
    try:
        from langchain_openai import ChatOpenAI
        
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced ChatOpenAI.ainvoke"""
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'gpt-3.5-turbo'))
            
            # Convert input to messages
            if hasattr(input, '__iter__') and not isinstance(input, str):
                messages = list(input)
            else:
                messages = [{"role": "user", "content": str(input)}]
            
            t0_ns = _emit_openai_call("ChatOpenAI.ainvoke", model_name, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                _emit_openai_return(t0_ns, "ChatOpenAI.ainvoke", result)
                return result
            except Exception as error:
                _emit_openai_return(t0_ns, "ChatOpenAI.ainvoke", None, str(error))
                raise
        
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
        
    except Exception as e:
        pass

def _patch_chatanthropic():
    """Actually patch ChatAnthropic.ainvoke"""
    try:
        from langchain_anthropic import ChatAnthropic
        
        original_ainvoke = ChatAnthropic.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'claude'))
            
            if hasattr(input, '__iter__') and not isinstance(input, str):
                messages = list(input)
            else:
                messages = [{"role": "user", "content": str(input)}]
            
            t0_ns = _emit_openai_call("ChatAnthropic.ainvoke", model_name, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                _emit_openai_return(t0_ns, "ChatAnthropic.ainvoke", result)
                return result
            except Exception as error:
                _emit_openai_return(t0_ns, "ChatAnthropic.ainvoke", None, str(error))
                raise
        
        ChatAnthropic.ainvoke = traced_ainvoke
        ChatAnthropic._handit_patched = True
        
    except Exception as e:
        pass
