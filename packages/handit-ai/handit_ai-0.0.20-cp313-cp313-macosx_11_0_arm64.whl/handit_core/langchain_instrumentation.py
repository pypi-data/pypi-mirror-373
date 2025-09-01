"""
LangChain instrumentation for handit_ai
Manually instruments LangChain ainvoke calls to ensure they're captured
"""
import time
import json
from typing import Any, Optional
import contextvars

# Get the active session ID from the native module
_active_session_id = contextvars.ContextVar('active_session_id', default=None)
_native = None

def _get_native():
    """Lazy load the native module"""
    global _native
    if _native is None:
        try:
            import handit_core.handit_core_native as native
            _native = native
        except ImportError:
            _native = False
    return _native

def _get_active_session():
    """Get active session ID"""
    try:
        native = _get_native()
        if native and hasattr(native, 'get_active_session_id_py'):
            return native.get_active_session_id_py()
    except:
        pass
    return None

def _emit_langchain_call(method_name: str, model: str, messages: list, **kwargs) -> int:
    """Emit a call event for LangChain ainvoke"""
    sid = _get_active_session()
    if not sid or not _get_native():
        return 0
    
    t0 = time.time_ns()
    try:
        _native_on = getattr(_get_native(), "on_call_with_args_py", None)
        if _native_on is None:
            return 0
        
        func_name = method_name
        module_name = "langchain.chat_models"
        file_name = "<langchain-api>"
        line_no = 1
        
        # Build args preview
        args_preview = {
            "model": model,
            "messages": str(messages),
            **{k: str(v) for k, v in kwargs.items() if k in ["temperature", "max_tokens", "timeout"]}
        }
        
        args_json_str = json.dumps(args_preview)
        _native_on(sid, func_name, module_name, file_name, line_no, t0, args_json_str)
        return t0
    except Exception:
        return 0

def _emit_langchain_return(t0_ns: int, func_name: str, result: Any, error: Optional[str] = None) -> None:
    """Emit a return event for LangChain ainvoke"""
    sid = _get_active_session()
    if not sid or not _get_native() or t0_ns == 0:
        return
    
    t1 = time.time_ns()
    try:
        _native_off = getattr(_get_native(), "on_return_with_preview_py", None)
        if _native_off is None:
            return
        
        dt_ns = t1 - t0_ns
        if error:
            locals_preview = {"return": f"Error: {error}"}
        else:
            try:
                if hasattr(result, 'content'):
                    content = result.content or ""
                    locals_preview = {"return": content}
                else:
                    locals_preview = {"return": str(result)}
            except Exception:
                locals_preview = {"return": "<langchain-response>"}
        
        preview_json_str = json.dumps(locals_preview)
        _native_off(sid, func_name, int(t1), int(dt_ns), preview_json_str)
    except Exception:
        pass

def patch_langchain():
    """Patch LangChain ChatOpenAI and other chat models to emit events"""
    try:
        # Patch ChatOpenAI
        from langchain_openai import ChatOpenAI
        
        if hasattr(ChatOpenAI, '_handit_patched'):
            return
        
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, messages, **kwargs):
            """Traced version of ChatOpenAI.ainvoke"""
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'unknown'))
            
            # Emit call event
            t0_ns = _emit_langchain_call("ChatOpenAI.ainvoke", model_name, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, messages, **kwargs)
                _emit_langchain_return(t0_ns, "ChatOpenAI.ainvoke", result)
                return result
            except Exception as error:
                _emit_langchain_return(t0_ns, "ChatOpenAI.ainvoke", None, str(error))
                raise
        
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
        
    except ImportError:
        pass  # LangChain not available
    except Exception as e:
        pass  # Silent fail to not break user code
    
    # Also patch other common LangChain models
    try:
        from langchain_anthropic import ChatAnthropic
        if not hasattr(ChatAnthropic, '_handit_patched'):
            original_ainvoke = ChatAnthropic.ainvoke
            
            async def traced_anthropic_ainvoke(self, messages, **kwargs):
                model_name = getattr(self, 'model_name', getattr(self, 'model', 'claude'))
                t0_ns = _emit_langchain_call("ChatAnthropic.ainvoke", model_name, messages, **kwargs)
                try:
                    result = await original_ainvoke(self, messages, **kwargs)
                    _emit_langchain_return(t0_ns, "ChatAnthropic.ainvoke", result)
                    return result
                except Exception as error:
                    _emit_langchain_return(t0_ns, "ChatAnthropic.ainvoke", None, str(error))
                    raise
            
            ChatAnthropic.ainvoke = traced_anthropic_ainvoke
            ChatAnthropic._handit_patched = True
    except ImportError:
        pass

def patch_langgraph():
    """Patch LangGraph CompiledGraph ainvoke calls"""
    try:
        from langgraph.graph.graph import CompiledGraph
        
        if hasattr(CompiledGraph, '_handit_patched'):
            return
        
        original_ainvoke = CompiledGraph.ainvoke
        
        async def traced_graph_ainvoke(self, input_data, **kwargs):
            """Traced version of CompiledGraph.ainvoke"""
            
            # Emit call event
            t0_ns = _emit_langchain_call("graph_ainvoke", "langgraph", [input_data], **kwargs)
            
            try:
                result = await original_ainvoke(self, input_data, **kwargs)
                _emit_langchain_return(t0_ns, "graph_ainvoke", result)
                return result
            except Exception as error:
                _emit_langchain_return(t0_ns, "graph_ainvoke", None, str(error))
                raise
        
        CompiledGraph.ainvoke = traced_graph_ainvoke
        CompiledGraph._handit_patched = True
        
    except ImportError:
        pass
    except Exception as e:
        pass

def enable_langchain_tracing():
    """Enable comprehensive LangChain/LangGraph tracing"""
    try:
        patch_langchain()
        patch_langgraph()
    except Exception as e:
        pass

# Test with manual patching
async def test_with_patching():
    """Test LangChain with manual patching enabled"""
    enable_langchain_tracing()
    
    if not LANGCHAIN_AVAILABLE:
        return
    
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    
    # Test direct ChatOpenAI call
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="sk-test-key-not-real")
    
    try:
        await llm.ainvoke([HumanMessage(content="Hello!")])
    except Exception as e:
        pass

async def main():
    """Main function"""
    
    with session(tag="langchain-patched-test"):
        await test_with_patching()
    

if __name__ == "__main__":
    asyncio.run(main())
