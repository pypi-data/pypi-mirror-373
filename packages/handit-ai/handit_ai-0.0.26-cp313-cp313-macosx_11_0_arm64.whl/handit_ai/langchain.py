"""
LangChain integration for handit_ai
Users can optionally import this to enable LangChain ainvoke tracing
"""
import time
import json
from typing import Any

def enable_langchain_tracing():
    """
    Enable automatic LangChain ainvoke tracing
    
    Usage:
        from handit_ai.langchain import enable_langchain_tracing
        enable_langchain_tracing()
        
        # Now all ChatOpenAI.ainvoke calls will be traced automatically
    """
    _patch_chatopenai()
    _patch_chatanthropic()

def _patch_chatopenai():
    """Patch ChatOpenAI.ainvoke to emit tracing events"""
    try:
        from langchain_openai import ChatOpenAI
        
        if hasattr(ChatOpenAI, '_handit_patched'):
            return
        
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced version of ChatOpenAI.ainvoke"""
            
            # Check for active session
            try:
                import handit_core.handit_core_native as native
                session_id = native.get_active_session_id_py()
                if not session_id:
                    # No session, just call original
                    return await original_ainvoke(self, input, config, **kwargs)
            except:
                # No native module, call original
                return await original_ainvoke(self, input, config, **kwargs)
            
            # Extract model info
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'gpt-3.5-turbo'))
            
            # Start timing
            t0_ns = time.time_ns()
            
            # Emit call event
            try:
                # Format input for logging
                if hasattr(input, '__iter__') and not isinstance(input, str):
                    input_preview = str(list(input))[:300]
                else:
                    input_preview = str(input)[:300]
                
                args_preview = {
                    "model": model_name,
                    "input": input_preview,
                    **{k: str(v)[:100] for k, v in kwargs.items() if k in ["temperature", "max_tokens", "stream"]}
                }
                
                native.on_call_with_args_py(
                    session_id,
                    "ChatOpenAI.ainvoke",
                    "langchain_openai",
                    "<langchain>",
                    1,
                    t0_ns,
                    json.dumps(args_preview)
                )
            except Exception:
                pass
            
            try:
                # Call original method
                result = await original_ainvoke(self, input, config, **kwargs)
                
                # Emit return event
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    
                    # Extract response content
                    if hasattr(result, 'content'):
                        response_content = result.content[:500] if result.content else "<empty>"
                    elif hasattr(result, 'text'):
                        response_content = result.text[:500] if result.text else "<empty>"
                    else:
                        response_content = str(result)[:500]
                    
                    return_preview = {"return": response_content}
                    
                    native.on_return_with_preview_py(
                        session_id,
                        "ChatOpenAI.ainvoke",
                        t1_ns,
                        dt_ns,
                        json.dumps(return_preview)
                    )
                except Exception:
                    pass
                
                return result
                
            except Exception as error:
                # Emit error return event
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    error_preview = {"return": f"Error: {str(error)[:200]}"}
                    
                    native.on_return_with_preview_py(
                        session_id,
                        "ChatOpenAI.ainvoke",
                        t1_ns,
                        dt_ns,
                        json.dumps(error_preview)
                    )
                except Exception:
                    pass
                
                raise
        
        # Apply the patch
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
        
    except ImportError:
        pass
    except Exception as e:
        pass

def _patch_chatanthropic():
    """Patch ChatAnthropic.ainvoke to emit tracing events"""
    try:
        from langchain_anthropic import ChatAnthropic
        
        if hasattr(ChatAnthropic, '_handit_patched'):
            return
        
        original_ainvoke = ChatAnthropic.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced version of ChatAnthropic.ainvoke"""
            
            # Check for active session
            try:
                import handit_core.handit_core_native as native
                session_id = native.get_active_session_id_py()
                if not session_id:
                    return await original_ainvoke(self, input, config, **kwargs)
            except:
                return await original_ainvoke(self, input, config, **kwargs)
            
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'claude'))
            t0_ns = time.time_ns()
            
            # Emit call event
            try:
                if hasattr(input, '__iter__') and not isinstance(input, str):
                    input_preview = str(list(input))[:300]
                else:
                    input_preview = str(input)[:300]
                
                args_preview = {"model": model_name, "input": input_preview}
                native.on_call_with_args_py(session_id, "ChatAnthropic.ainvoke", "langchain_anthropic", "<langchain>", 1, t0_ns, json.dumps(args_preview))
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
                    native.on_return_with_preview_py(session_id, "ChatAnthropic.ainvoke", t1_ns, dt_ns, json.dumps(return_preview))
                except:
                    pass
                
                return result
            except Exception as error:
                try:
                    t1_ns = time.time_ns()
                    dt_ns = t1_ns - t0_ns
                    error_preview = {"return": f"Error: {str(error)[:200]}"}
                    native.on_return_with_preview_py(session_id, "ChatAnthropic.ainvoke", t1_ns, dt_ns, json.dumps(error_preview))
                except:
                    pass
                raise
        
        ChatAnthropic.ainvoke = traced_ainvoke
        ChatAnthropic._handit_patched = True
        
    except ImportError:
        pass
    except Exception as e:
        pass
