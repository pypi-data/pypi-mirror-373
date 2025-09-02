from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
	from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
	_native = None  # type: ignore

from . import _active_session_id  # type: ignore

REDACT_QUERY = True
DEFAULT_TIMEOUT = 50.0  # seconds


def _emit_request(method: str, url: str, headers: Optional[Dict[str, Any]], bytes_out: Optional[int], request_body: Optional[str]) -> int:
	# Try to get session ID from multiple sources (for thread compatibility)
	sid = _active_session_id.get()
	
	# If no session in current thread, try to get from global session (worker threads)
	if not sid and _native is not None:
		try:
			# Check if there's a global session we can use
			if hasattr(_native, 'get_active_session_id_py'):
				result = _native.get_active_session_id_py()
				if result:
					sid = result
		except:
			pass
	
	# If still no session, create a temporary one for worker thread calls
	if not sid:
		# For worker threads, use a special session ID to capture orphaned calls
		sid = "worker-thread-calls"
	
	if _native is None:
		return 0
	t0 = time.time_ns()
	_native_on = getattr(_native, "on_http_request_py", None)
	if _native_on is None:
		return 0
	
	_native_on(sid, method, url, t0, headers or {}, bytes_out or 0, request_body)
	return t0


def _emit_response(t0_ns: int, status: int, headers: Optional[Dict[str, Any]], bytes_in: Optional[int], error: Optional[str], response_body: Optional[str]) -> None:
	# Try to get session ID from multiple sources (for thread compatibility)
	sid = _active_session_id.get()
	
	# If no session in current thread, try to get from global session (worker threads)
	if not sid and _native is not None:
		try:
			if hasattr(_native, 'get_active_session_id_py'):
				result = _native.get_active_session_id_py()
				if result:
					sid = result
		except:
			pass
	
	# If still no session, use worker thread session for orphaned calls
	if not sid:
		sid = "worker-thread-calls"
	
	if _native is None:
		return
	t1 = time.time_ns()
	_native_off = getattr(_native, "on_http_response_py", None)
	if _native_off is None:
		return
	
	_native_off(sid, status, t1, t1 - t0_ns, headers or {}, bytes_in or 0, error, response_body)


# requests instrumentation

def patch_requests() -> None:
	try:
		import requests
		from requests.sessions import Session
		from requests import Timeout
	except Exception:
		return

	# Prevent double patching
	if getattr(Session.request, "_handit_patched", False):
		return

	orig = Session.request

	def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Set a default timeout if not provided
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = DEFAULT_TIMEOUT
		# Extract request body (best-effort)
		body_str = None
		data = kwargs.get("data")
		json_data = kwargs.get("json")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif data is not None:
			try:
				if isinstance(data, (bytes, bytearray)):
					body_str = data.decode("utf-8", errors="replace")
				else:
					body_str = str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, url, kwargs.get("headers"), None, body_str)
		# Suppress profiler while executing the HTTP client's internals
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				content = getattr(resp, "content", None)
				if content is not None:
					resp_body = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(getattr(resp, "content", b"")) if getattr(resp, "content", None) is not None else None, None, resp_body)
			return resp
		except Timeout as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	Session.request = wrapped  # type: ignore


# httpx instrumentation (sync only here)

def patch_httpx() -> None:
	try:
		import httpx
	except Exception:
		return

	# Patch sync client
	if not getattr(httpx.Client.request, "_handit_patched", False):
		_patch_httpx_sync()
	
	# Patch async client  
	if not getattr(httpx.AsyncClient.request, "_handit_patched", False):
		_patch_httpx_async()
	
	# Patch OpenAI's base client (the actual HTTP layer LangChain uses)
	try:
		import openai._base_client
		
		# Patch the sync base client
		if hasattr(openai._base_client, 'SyncHttpxClientWrapper'):
			_patch_openai_httpx_wrapper()
		
		# Patch the async base client (this is what LangChain actually uses)
		if hasattr(openai._base_client, 'AsyncAPIClient'):
			_patch_openai_async_base_client()
		
		# Also patch the httpx client wrappers
		import openai
		if hasattr(openai, 'DefaultAsyncHttpxClient'):
			_patch_openai_async_httpx_wrapper()
	except:
		pass
	
	# CRITICAL: Patch LangChain's own HTTP client wrappers
	try:
		import langchain_openai.chat_models._client_utils
		_patch_langchain_sync_httpx_wrapper()
		_patch_langchain_async_httpx_wrapper()
	except:
		pass


def _patch_httpx_sync() -> None:
	import httpx
	orig = httpx.Client.request

	def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Respect existing timeouts; set a default if none
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = httpx.Timeout(DEFAULT_TIMEOUT)
		# Extract httpx request body
		body_str = None
		content = kwargs.get("content")
		json_data = kwargs.get("json")
		data = kwargs.get("data")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif content is not None:
			try:
				body_str = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				body_str = "<unrepr>"
		elif data is not None:
			try:
				body_str = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, body_str)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				if hasattr(resp, "content"):
					resp_body = resp.content.decode("utf-8", errors="replace") if isinstance(resp.content, (bytes, bytearray)) else str(resp.content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(resp.content) if hasattr(resp, "content") else None, None, resp_body)
			return resp
		except httpx.TimeoutException as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	httpx.Client.request = wrapped  # type: ignore


def _patch_httpx_async() -> None:
	import httpx
	orig = httpx.AsyncClient.request

	async def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Respect existing timeouts; set a default if none
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = httpx.Timeout(DEFAULT_TIMEOUT)
		# Extract httpx request body
		body_str = None
		content = kwargs.get("content")
		json_data = kwargs.get("json")
		data = kwargs.get("data")
		if json_data is not None:
			try:
				import json as _json
				body_str = _json.dumps(json_data)
			except Exception:
				body_str = str(json_data)
		elif content is not None:
			try:
				body_str = content.decode("utf-8", errors="replace") if isinstance(content, (bytes, bytearray)) else str(content)
			except Exception:
				body_str = "<unrepr>"
		elif data is not None:
			try:
				body_str = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
			except Exception:
				body_str = "<unrepr>"
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, body_str)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = await orig(self, method, url, *args, **kwargs)
			resp_body = None
			try:
				if hasattr(resp, "content"):
					resp_body = resp.content.decode("utf-8", errors="replace") if isinstance(resp.content, (bytes, bytearray)) else str(resp.content)
			except Exception:
				resp_body = "<unrepr>"
			_emit_response(t0, resp.status_code, dict(resp.headers), len(resp.content) if hasattr(resp, "content") else None, None, resp_body)
			return resp
		except httpx.TimeoutException as e:
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	httpx.AsyncClient.request = wrapped  # type: ignore

def _patch_openai_httpx_wrapper() -> None:
	"""Patch OpenAI's SyncHttpxClientWrapper used by LangChain"""
	try:
		import openai._base_client
		
		wrapper_class = openai._base_client.SyncHttpxClientWrapper
		if getattr(wrapper_class.request, "_handit_patched", False):
			return
		
		orig = wrapper_class.request
		
		def wrapped(self, method, url, *args, **kwargs):
			"""Wrapped OpenAI httpx request"""
			# Extract headers and body
			headers = kwargs.get("headers", {})
			body_str = None
			
			# Try to get request body
			if "content" in kwargs:
				content = kwargs["content"]
				if isinstance(content, (str, bytes)):
					body_str = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
			elif "json" in kwargs:
				try:
					import json
					body_str = json.dumps(kwargs["json"])
				except:
					body_str = str(kwargs["json"])
			
			# Emit request
			t0 = _emit_request(method, str(url), headers, len(body_str.encode()) if body_str else 0, body_str)
			
			try:
				response = orig(self, method, url, *args, **kwargs)
				
				# Extract response details
				status = getattr(response, "status_code", 0)
				resp_headers = getattr(response, "headers", {})
				resp_content = None
				
				try:
					if hasattr(response, "text"):
						resp_content = response.text
					elif hasattr(response, "content"):
						content = response.content
						resp_content = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
				except:
					resp_content = "<response-content>"
				
				_emit_response(t0, status, resp_headers, len(resp_content) if resp_content else 0, None, resp_content)
				return response
				
			except Exception as e:
				_emit_response(t0, 0, {}, 0, str(e), None)
				raise
		
		wrapper_class.request = wrapped
		wrapper_class.request._handit_patched = True
		
	except Exception as e:
		pass

def _patch_openai_async_httpx_wrapper() -> None:
	"""Patch OpenAI's DefaultAsyncHttpxClient used by LangChain"""
	try:
		import openai
		
		wrapper_class = openai.DefaultAsyncHttpxClient
		if getattr(wrapper_class.request, "_handit_patched", False):
			return
		
		orig = wrapper_class.request
		
		async def wrapped(self, method, url, *args, **kwargs):
			"""Wrapped OpenAI async httpx request"""
			# Extract headers and body
			headers = kwargs.get("headers", {})
			body_str = None
			
			# Try to get request body
			if "content" in kwargs:
				content = kwargs["content"]
				if isinstance(content, (str, bytes)):
					body_str = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
			elif "json" in kwargs:
				try:
					import json
					body_str = json.dumps(kwargs["json"])
				except:
					body_str = str(kwargs["json"])
			
			# Emit request
			t0 = _emit_request(method, str(url), headers, len(body_str.encode()) if body_str else 0, body_str)
			
			try:
				response = await orig(self, method, url, *args, **kwargs)
				
				# Extract response details
				status = getattr(response, "status_code", 0)
				resp_headers = getattr(response, "headers", {})
				resp_content = None
				
				try:
					if hasattr(response, "text"):
						resp_content = response.text
					elif hasattr(response, "content"):
						content = response.content
						resp_content = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
				except:
					resp_content = "<response-content>"
				
				_emit_response(t0, status, resp_headers, len(resp_content) if resp_content else 0, None, resp_content)
				return response
				
			except Exception as e:
				_emit_response(t0, 0, {}, 0, str(e), None)
				raise
		
		wrapper_class.request = wrapped
		wrapper_class.request._handit_patched = True
		
	except Exception as e:
		pass

def _patch_openai_async_base_client() -> None:
	"""Patch OpenAI's AsyncAPIClient.request - the actual HTTP layer LangChain uses"""
	try:
		import openai._base_client
		
		base_client_class = openai._base_client.AsyncAPIClient
		if getattr(base_client_class.request, "_handit_patched", False):
			return
		
		orig = base_client_class.request
		
		async def wrapped(self, cast_to, options, *, stream=None, stream_cls=None):
			"""Wrapped OpenAI AsyncAPIClient.request - captures LangChain calls"""
			
			# Extract request details
			method = getattr(options, 'method', 'POST')
			url = getattr(options, 'url', 'unknown')
			headers = getattr(options, 'headers', {})
			
			# Try to extract JSON body
			body_str = None
			if hasattr(options, 'json_data') and options.json_data:
				try:
					import json
					body_str = json.dumps(options.json_data)
				except:
					body_str = str(options.json_data)
			elif hasattr(options, 'content') and options.content:
				body_str = str(options.content)
			
			# Emit request event
			t0 = _emit_request(method, str(url), headers, len(body_str.encode()) if body_str else 0, body_str)
			
			try:
				# Call original method
				response = await orig(self, cast_to, options, stream=stream, stream_cls=stream_cls)
				
				# Extract response details
				status = 200  # Assume success if no exception
				resp_headers = {}
				resp_content = None
				
				# Try to extract response content
				try:
					# Try to get the full response content without truncation
					if hasattr(response, 'choices') and response.choices:
						# This is a chat completion response - get the actual content
						choice = response.choices[0]
						if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
							resp_content = choice.message.content
						else:
							resp_content = str(response)
					elif hasattr(response, 'content'):
						resp_content = str(response.content)
					elif hasattr(response, 'text'):
						resp_content = response.text
					elif hasattr(response, 'model_dump'):
						# Pydantic model - get full content
						import json
						resp_content = json.dumps(response.model_dump())
					else:
						resp_content = str(response)
				except Exception as e:
					resp_content = f"<response-extraction-error: {str(e)}>"
				
				_emit_response(t0, status, resp_headers, len(resp_content) if resp_content else 0, None, resp_content)
				return response
				
			except Exception as e:
				_emit_response(t0, 401, {}, 0, str(e), None)
				raise
		
		base_client_class.request = wrapped
		base_client_class.request._handit_patched = True
		
	except Exception as e:
		pass


def _patch_langchain_sync_httpx_wrapper() -> None:
	"""Patch LangChain's custom _SyncHttpxClientWrapper - the ACTUAL client used by LangChain"""
	try:
		import langchain_openai.chat_models._client_utils
		
		wrapper_class = langchain_openai.chat_models._client_utils._SyncHttpxClientWrapper
		if getattr(wrapper_class.request, "_handit_patched", False):
			return
		
		orig = wrapper_class.request
		
		def wrapped(self, method, url, *args, **kwargs):
			"""Wrapped LangChain SyncHttpxClientWrapper.request - THIS IS WHERE LANGCHAIN CALLS GO"""
			
			# Extract headers and body  
			headers = kwargs.get("headers", {})
			body_str = None
			
			# Try to get request body
			if "content" in kwargs:
				content = kwargs["content"]
				if isinstance(content, (str, bytes)):
					body_str = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
			elif "json" in kwargs:
				try:
					import json
					body_str = json.dumps(kwargs["json"])
				except:
					body_str = str(kwargs["json"])
			
			# Emit request
			t0 = _emit_request(method, str(url), headers, len(body_str.encode()) if body_str else 0, body_str)
			
			try:
				response = orig(self, method, url, *args, **kwargs)
				
				# Extract response details
				status = getattr(response, "status_code", 0)
				resp_headers = getattr(response, "headers", {})
				resp_content = None
				
				try:
					if hasattr(response, "text"):
						resp_content = response.text
					elif hasattr(response, "content"):
						content = response.content
						resp_content = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
				except:
					resp_content = "<langchain-response>"
				
				_emit_response(t0, status, resp_headers, len(resp_content) if resp_content else 0, None, resp_content)
				return response
				
			except Exception as e:
				_emit_response(t0, 0, {}, 0, str(e), None)
				raise
		
		wrapper_class.request = wrapped
		wrapper_class.request._handit_patched = True
		
	except Exception as e:
		pass


def _patch_langchain_async_httpx_wrapper() -> None:
	"""Patch LangChain's custom _AsyncHttpxClientWrapper - for async LangChain calls"""
	try:
		import langchain_openai.chat_models._client_utils
		
		wrapper_class = langchain_openai.chat_models._client_utils._AsyncHttpxClientWrapper
		if getattr(wrapper_class.request, "_handit_patched", False):
			return
		
		orig = wrapper_class.request
		
		async def wrapped(self, method, url, *args, **kwargs):
			"""Wrapped LangChain AsyncHttpxClientWrapper.request - for async ainvoke calls"""
			
			# Extract headers and body  
			headers = kwargs.get("headers", {})
			body_str = None
			
			# Try to get request body
			if "content" in kwargs:
				content = kwargs["content"]
				if isinstance(content, (str, bytes)):
					body_str = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
			elif "json" in kwargs:
				try:
					import json
					body_str = json.dumps(kwargs["json"])
				except:
					body_str = str(kwargs["json"])
			
			# Emit request
			t0 = _emit_request(method, str(url), headers, len(body_str.encode()) if body_str else 0, body_str)
			
			try:
				response = await orig(self, method, url, *args, **kwargs)
				
				# Extract response details
				status = getattr(response, "status_code", 0)
				resp_headers = getattr(response, "headers", {})
				resp_content = None
				
				try:
					if hasattr(response, "text"):
						resp_content = response.text
					elif hasattr(response, "content"):
						content = response.content
						resp_content = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
				except:
					resp_content = "<langchain-async-response>"
				
				_emit_response(t0, status, resp_headers, len(resp_content) if resp_content else 0, None, resp_content)
				return response
				
			except Exception as e:
				_emit_response(t0, 0, {}, 0, str(e), None)
				raise
		
		wrapper_class.request = wrapped
		wrapper_class.request._handit_patched = True
		
	except Exception as e:
		pass


# aiohttp basic instrumentation (only wrap _request)

def patch_aiohttp() -> None:
	try:
		import aiohttp
		import asyncio  # for TimeoutError reference
	except Exception:
		return

	# Prevent double patching
	if getattr(aiohttp.ClientSession._request, "_handit_patched", False):
		return

	orig = aiohttp.ClientSession._request

	async def wrapped(self, method, url, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Set default timeout if not provided
		if "timeout" not in kwargs or kwargs["timeout"] is None:
			kwargs["timeout"] = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
		# For aiohttp we cannot read the request body here reliably; leave as None
		t0 = _emit_request(method, str(url), kwargs.get("headers"), None, None)
		_suppress_enter = getattr(_native, "suppress_profiler_enter_py", None) if _native is not None else None
		_suppress_exit = getattr(_native, "suppress_profiler_exit_py", None) if _native is not None else None
		if callable(_suppress_enter):
			try:
				_suppress_enter()
			except Exception:
				pass
		try:
			resp = await orig(self, method, url, *args, **kwargs)
			try:
				# consume headers only; body not read here
				# To avoid consuming the stream, don't read body here. Users can opt in with middleware later.
				_emit_response(t0, resp.status, dict(resp.headers), None, None, None)
			except Exception:  # pragma: no cover
				pass
			return resp
		except asyncio.TimeoutError as e:  # type: ignore[name-defined]
			_emit_response(t0, 408, None, None, str(e), None)
			raise
		except Exception as e:  # noqa: BLE001
			_emit_response(t0, -1, None, None, str(e), None)
			raise
		finally:
			if callable(_suppress_exit):
				try:
					_suppress_profiler_exit = _suppress_exit
					_suppress_profiler_exit()
				except Exception:
					pass

	setattr(wrapped, "_handit_patched", True)
	setattr(wrapped, "_handit_orig", orig)
	aiohttp.ClientSession._request = wrapped  # type: ignore