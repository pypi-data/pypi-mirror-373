#[cfg(feature = "python")]
use pyo3::prelude::*;

use handit_core as core;
use handit_exporter as exporter;
use once_cell::sync::Lazy;
use regex::Regex;
use std::cell::RefCell;
use std::collections::HashMap;
use std::env;
use std::os::raw::c_int;
use std::ptr;
use std::sync::{Arc, Mutex};
use pyo3::{ffi, Bound};

#[cfg(feature = "python")]
struct CaptureConfig {
    max_str: usize,
    max_locals: usize,
    include: Option<Regex>,
    exclude: Option<Regex>,
    exclude_file_re: Option<Regex>,
    capture_only_cwd: bool,
    cwd_prefix: Option<String>,
    redact: Option<Regex>,
    sample_rate: f64,
}

#[cfg(feature = "python")]
static CFG: Lazy<CaptureConfig> = Lazy::new(|| {
    let max_str = env::var("HANDIT_MAX_STR").ok().and_then(|v| v.parse().ok()).unwrap_or(100000);
    let max_locals = env::var("HANDIT_MAX_LOCALS").ok().and_then(|v| v.parse().ok()).unwrap_or(100);
    let include = env::var("HANDIT_INCLUDE").ok().and_then(|p| Regex::new(&p).ok()).or_else(|| Regex::new(".*").ok());
    // Default exclude to avoid tracing stdlib/third-party noise (modules)
    // Explicitly exclude CPython's frozen import machinery as well
    let exclude_pattern = env::var("HANDIT_EXCLUDE").ok().unwrap_or_else(|| {
        // Note: deliberately NOT excluding generic `_.*` to avoid filtering `__main__`
        r"^(_frozen_importlib.*|_frozen_importlib_external.*|handit_core|handit|handit_core.http_instrumentation|requests|urllib3|httpx|httpcore|ssl|socket|select|concurrent|threading|importlib|site|encodings|pkg_resources|zipimport|json|logging|re|typing|types|collections|contextlib|inspect|abc|functools|itertools|weakref|dotenv|openai)::|namedtuple_.*::|.*::<lambda>|.*::is_annotated|.*::is_self|.*::to_jsonable|.*::to_json_string|.*::<dictcomp>|anyio\._backends\._asyncio::<module>".to_string()
    });
    let exclude = Regex::new(&exclude_pattern).ok();
    // Default file path exclude to skip site-packages/dist-packages and stdlib directories
    // Also exclude any synthetic CPython paths like "<frozen importlib._bootstrap>"
    let exclude_file_pattern = env::var("HANDIT_EXCLUDE_FILES").ok().unwrap_or_else(|| {
        r"(^<frozen .*>$)|(^<string>$)|(?i)(/|\\)(site-packages|dist-packages)(/|\\)|(/|\\)lib(/|\\)python".to_string()
    });
    let exclude_file_re = Regex::new(&exclude_file_pattern).ok();
    // Capture only files under current working directory by default (can be disabled via env)
    let capture_only_cwd = env::var("HANDIT_CAPTURE_ONLY_CWD").ok().and_then(|v| v.parse().ok()).unwrap_or(false);
    let cwd_prefix = std::env::current_dir().ok().map(|p| {
        let mut s = p.to_string_lossy().to_string();
        if !s.ends_with('/') && !s.ends_with('\\') { s.push('/'); }
        s
    });
    let redact_pattern = env::var("HANDIT_REDACT").ok().unwrap_or_else(|| {
        // Default redaction for API keys, tokens, passwords, and other sensitive data
        r"(?i)(api_key|token|password|secret|auth|bearer|key|credential|sk-|pk-|xoxb-|xoxp-)".to_string()
    });
    let redact = Regex::new(&redact_pattern).ok();
    let sample_rate = env::var("HANDIT_SAMPLE_RATE").ok().and_then(|v| v.parse().ok()).unwrap_or(1.0);
    CaptureConfig { max_str, max_locals, include, exclude, exclude_file_re, capture_only_cwd, cwd_prefix, redact, sample_rate }
});

#[cfg(feature = "python")]
fn should_capture(func_name: &str, module_name: &str, file_name: &str) -> bool {
    let path = format!("{}::{}", module_name, func_name);
    if let Some(ex) = &CFG.exclude { if ex.is_match(&path) { return false; } }
    if let Some(inc) = &CFG.include { if !inc.is_match(&path) { return false; } }
    // Exclude by file path patterns
    if let Some(re) = &CFG.exclude_file_re { if re.is_match(file_name) { return false; } }
    // Limit to current working directory by default unless an include is provided
    if CFG.capture_only_cwd && CFG.include.is_none() {
        if let Some(prefix) = &CFG.cwd_prefix {
            if !file_name.starts_with(prefix) { return false; }
        }
    }
    if CFG.sample_rate < 1.0 {
        // Simple hash-based sampling
        let h = seahash::hash(path.as_bytes());
        let frac = h as f64 / u64::MAX as f64;
        return frac < CFG.sample_rate;
    }
    true
}

#[cfg(feature = "python")]
fn cap_string(s: &str, max_len: usize) -> String {
    if s.len() <= max_len { s.to_string() } else { format!("{}…", &s[..max_len]) }
}

#[cfg(feature = "python")]
fn maybe_redact(key: &str, val: String) -> String {
    if let Some(r) = &CFG.redact {
        // Check both key names and values for sensitive patterns
        if r.is_match(key) || r.is_match(&val) { 
            return "<redacted>".to_string(); 
        }
    }
    val
}

#[cfg(feature = "python")]
fn preview_any(any: &Bound<'_, pyo3::types::PyAny>, max_str: usize) -> serde_json::Value {
    match any.str() {
        Ok(s) => serde_json::Value::String(cap_string(&s.to_string_lossy(), max_str)),
        Err(_) => serde_json::Value::String("<unrepr>".to_string()),
    }
}

#[cfg(feature = "python")]
fn build_args_preview(frame: &Bound<'_, pyo3::types::PyAny>) -> serde_json::Value {
    let mut map = serde_json::Map::new();
    if let (Ok(code), Ok(locals)) = (frame.getattr("f_code"), frame.getattr("f_locals")) {
        if let (Ok(names_any), Ok(argcount_any)) = (code.getattr("co_varnames"), code.getattr("co_argcount")) {
            if let (Ok(names), Ok(argcount)) = (names_any.downcast::<pyo3::types::PyTuple>(), argcount_any.extract::<usize>()) {
                let limit = argcount.min(names.len()).min(CFG.max_locals);
                for i in 0..limit {
                    if let Ok(name) = names.get_item(i).unwrap().extract::<String>() {
                        if let Ok(value) = locals.get_item(&name) {
                            let v = preview_any(&value, CFG.max_str);
                            map.insert(name.clone(), serde_json::Value::String(maybe_redact(&name, v.as_str().unwrap_or("").to_string())));
                        }
                    }
                }
            }
        }
    }
    serde_json::Value::Object(map)
}

#[cfg(feature = "python")]
fn build_locals_preview(frame: &Bound<'_, pyo3::types::PyAny>) -> serde_json::Value {
    let mut map = serde_json::Map::new();
    if let Ok(locals) = frame.getattr("f_locals") {
        if let Ok(dict) = locals.downcast::<pyo3::types::PyDict>() {
            for (k, v) in dict.iter().take(CFG.max_locals) {
                let key = k.str().map(|s| s.to_string()).unwrap_or_else(|_| "<key>".to_string());
                let pv = preview_any(&v, CFG.max_str);
                map.insert(key.clone(), serde_json::Value::String(maybe_redact(&key, pv.as_str().unwrap_or("").to_string())));
            }
        }
    }
    serde_json::Value::Object(map)
}

#[cfg(feature = "python")]
#[pyfunction]
fn start_session_py(tag: Option<String>, attrs: Option<std::collections::HashMap<String, String>>, traceparent: Option<String>, _span_id: Option<String>) -> PyResult<String> {
    let attrs = attrs.unwrap_or_default();
    // Parse traceparent if provided (version 00: traceparent: 00-<trace_id>-<span_id>-<flags>)
    let (trace_id, span_id) = if let Some(tp) = traceparent {
        let parts: Vec<&str> = tp.split('-').collect();
        if parts.len() >= 4 { (Some(parts[1].to_string()), Some(parts[2].to_string())) } else { (None, None) }
    } else { (None, None) };
    let handle = core::start_session(tag, attrs, trace_id, span_id);
    Ok(handle.session_id)
}

#[cfg(feature = "python")]
#[pyfunction]
fn on_call_py(session_id: String, func: String, module: String, file: String, line: u32, t0_ns: u128) -> PyResult<()> {
    core::on_call_by_id(&session_id, &func, &module, &file, line, t0_ns);
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn on_return_py(session_id: String, func: String, t1_ns: u128, dt_ns: u128) -> PyResult<()> {
    core::on_return_by_id(&session_id, &func, t1_ns, dt_ns);
    Ok(())
}

#[pyfunction]
fn on_call_with_args_py(session_id: String, func: String, module: String, file: String, line: u32, t0_ns: u128, args_preview_json: String) -> PyResult<()> {
    // Parse the JSON string back to serde_json::Value
    let args_preview: serde_json::Value = serde_json::from_str(&args_preview_json)
        .unwrap_or_else(|_| serde_json::json!({}));
    core::on_call_with_args_preview_by_id(&session_id, &func, &module, &file, line, t0_ns, args_preview);
    Ok(())
}

#[pyfunction]
fn on_return_with_preview_py(session_id: String, func: String, t1_ns: u128, dt_ns: u128, locals_preview_json: String) -> PyResult<()> {
    // Parse the JSON string back to serde_json::Value
    let locals_preview: serde_json::Value = serde_json::from_str(&locals_preview_json)
        .unwrap_or_else(|_| serde_json::json!({"return": "<parse-error>"}));
    core::on_return_with_locals_preview_by_id(&session_id, &func, t1_ns, dt_ns, locals_preview);
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn on_exception_py(session_id: String, func: String, type_name: String, message: String) -> PyResult<()> {
    core::on_exception_by_id(&session_id, &func, &type_name, &message);
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn on_http_request_py(session_id: String, method: String, url: String, t0_ns: u128, headers: pyo3::Py<pyo3::types::PyDict>, bytes_out: u64, request_body: Option<String>, py: Python<'_>) -> PyResult<()> {
    let headers_json = python_dict_to_json(py, &headers);
    core::http_request_by_id(&session_id, &method, &url, t0_ns, Some(headers_json), Some(bytes_out), request_body);
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn on_http_response_py(session_id: String, status: i32, t1_ns: u128, dt_ns: u128, headers: pyo3::Py<pyo3::types::PyDict>, bytes_in: u64, error: Option<String>, response_body: Option<String>, py: Python<'_>) -> PyResult<()> {
    let headers_json = python_dict_to_json(py, &headers);
    core::http_response_by_id(&session_id, status, t1_ns, dt_ns, Some(headers_json), Some(bytes_in), error, response_body);
    Ok(())
}

#[cfg(feature = "python")]
fn python_dict_to_json(py: Python<'_>, dict: &pyo3::Py<pyo3::types::PyDict>) -> serde_json::Value {
    let d = dict.bind(py);
    let mut map = serde_json::Map::new();
    for (k, v) in d.iter() {
        let key = k.str().map(|s| s.to_string()).unwrap_or_else(|_| "<key>".to_string());
        let val_str = v.str().map(|s| s.to_string_lossy().to_string()).unwrap_or_else(|_| "<unrepr>".to_string());
        map.insert(key, serde_json::Value::String(val_str));
    }
    serde_json::Value::Object(map)
}

// ---- Native profiler using CPython C-API ----
#[cfg(feature = "python")]
thread_local! {
    static ACTIVE_SESSION_ID: RefCell<Option<String>> = RefCell::new(None);
    static CALL_T0: RefCell<HashMap<usize, u128>> = RefCell::new(HashMap::new());
    static SUPPRESS_COUNT: RefCell<u32> = RefCell::new(0);
}

// Global session context for cross-thread access
static GLOBAL_SESSION_ID: Lazy<Arc<Mutex<Option<String>>>> = Lazy::new(|| Arc::new(Mutex::new(None)));

// Thread hook state
static THREAD_HOOK_INSTALLED: Lazy<Arc<Mutex<bool>>> = Lazy::new(|| Arc::new(Mutex::new(false)));

#[cfg(feature = "python")]
fn install_thread_hook() {
    // Check if already installed
    if let Ok(mut installed) = THREAD_HOOK_INSTALLED.lock() {
        if *installed {
            return;
        }
        *installed = true;
    }
    
    // Install Python threading hook using Python's threading module
    Python::with_gil(|py| {
        let threading_module = py.import_bound("threading").ok();
        if let Some(threading) = threading_module {
            // Hook into Thread.__init__ to enable profiling on new threads
            let thread_class = threading.getattr("Thread").ok();
            if let Some(thread_cls) = thread_class {
                // This is a simplified approach - in practice, we'd need more complex hooking
                // For now, we'll focus on the HTTP instrumentation fix
            }
        }
    });
}

#[cfg(feature = "python")]
fn enable_profiling_on_current_thread() {
    // Enable profiling on the current thread with global session context
    if let Ok(global_session) = GLOBAL_SESSION_ID.lock() {
        if let Some(session_id) = global_session.clone() {
            ACTIVE_SESSION_ID.with(|cell| { 
                *cell.borrow_mut() = Some(session_id); 
            });
            unsafe { 
                ffi::PyEval_SetProfile(Some(profiler_callback), ptr::null_mut()); 
            }
        }
    }
}

#[cfg(feature = "python")]
unsafe extern "C" fn profiler_callback(
    _obj: *mut ffi::PyObject,
    frame: *mut ffi::PyFrameObject,
    what: c_int,
    arg: *mut ffi::PyObject,
) -> c_int {
    const PY_TRACE_CALL: c_int = 0;
    const PY_TRACE_EXCEPTION: c_int = 1;
    const PY_TRACE_RETURN: c_int = 3;

    let mut has_session = false;
    let mut session_id_buf = String::new();
    ACTIVE_SESSION_ID.with(|cell| {
        if let Some(s) = cell.borrow().as_ref() {
            has_session = true;
            session_id_buf.push_str(s);
        }
    });
    if !has_session { return 0; }

    // Respect suppression flag to avoid tracing library internals (e.g., HTTP clients)
    let suppressed = SUPPRESS_COUNT.with(|c| *c.borrow());
    if suppressed > 0 { return 0; }

    let py = Python::assume_gil_acquired();
    let frame_any: Bound<'_, pyo3::types::PyAny> = Bound::from_borrowed_ptr(py, frame as *mut ffi::PyObject);

    let (func_name, module_name, file_name, first_lineno) = match (
        frame_any.getattr("f_code"),
        frame_any.getattr("f_globals"),
    ) {
        (Ok(code), Ok(globals)) => {
            let name: String = code.getattr("co_name").and_then(|o| o.extract::<String>()).unwrap_or_else(|_| "<unknown>".to_string());
            let file: String = code.getattr("co_filename").and_then(|o| o.extract::<String>()).unwrap_or_else(|_| "<unknown>".to_string());
            let lineno = code.getattr("co_firstlineno").and_then(|o| o.extract::<u32>()).unwrap_or(0);
            let module: String = globals.get_item("__name__").and_then(|o| o.extract::<String>()).unwrap_or_else(|_| "<module>".to_string());
            (name, module, file, lineno)
        }
        _ => ("<unknown>".to_string(), "<module>".to_string(), "<unknown>".to_string(), 0),
    };

    let key = frame as usize;

    match what {
        PY_TRACE_CALL => {
            if !should_capture(&func_name, &module_name, &file_name) { return 0; }
            let t0 = core::now_ns();
            CALL_T0.with(|m| { m.borrow_mut().insert(key, t0); });
            // Build args preview (lightweight)
            let args_preview = build_args_preview(&frame_any);
            core::on_call_with_args_preview_by_id(&session_id_buf, &func_name, &module_name, &file_name, first_lineno, t0, args_preview);
        }
        PY_TRACE_RETURN => {
            if !should_capture(&func_name, &module_name, &file_name) { return 0; }
            let t1 = core::now_ns();
            let t0 = CALL_T0.with(|m| m.borrow_mut().remove(&key));
            if let Some(t0) = t0 {
                // Return value preview on return (only the returned value, not all locals)
                let ret_preview = if !arg.is_null() {
                    let arg_any: Bound<'_, pyo3::types::PyAny> = Bound::from_borrowed_ptr(py, arg as *mut ffi::PyObject);
                    let pv = preview_any(&arg_any, CFG.max_str);
                    let mut map = serde_json::Map::new();
                    // Apply redaction to return values that might contain sensitive data
                    let redacted_value = if let serde_json::Value::String(s) = &pv {
                        serde_json::Value::String(maybe_redact("return", s.clone()))
                    } else {
                        pv
                    };
                    map.insert("return".to_string(), redacted_value);
                    serde_json::Value::Object(map)
                } else {
                    let mut map = serde_json::Map::new();
                    map.insert("return".to_string(), serde_json::Value::String("<none>".to_string()));
                    serde_json::Value::Object(map)
                };
                core::on_return_with_locals_preview_by_id(&session_id_buf, &func_name, t1, t1 - t0, ret_preview);
            }
        }
        PY_TRACE_EXCEPTION => {
            if !should_capture(&func_name, &module_name, &file_name) { return 0; }
            let (type_name, msg) = if !arg.is_null() {
                let arg_any: Bound<'_, pyo3::types::PyAny> = Bound::from_borrowed_ptr(py, arg as *mut ffi::PyObject);
                if let Ok(tuple) = arg_any.downcast::<pyo3::types::PyTuple>() {
                    if tuple.len() >= 2 {
                        let type_obj = tuple.get_item(0).unwrap();
                        let exc_obj = tuple.get_item(1).unwrap();
                        let tn: String = type_obj.getattr("__name__").and_then(|o| o.extract::<String>()).unwrap_or_else(|_| "<exc>".to_string());
                        let ms = exc_obj.str().map(|s| s.to_string_lossy().to_string()).unwrap_or_default();
                        (tn, ms)
                    } else { ("<exc>".to_string(), String::new()) }
                } else { ("<exc>".to_string(), String::new()) }
            } else { ("<exc>".to_string(), String::new()) };
            core::on_exception_by_id(&session_id_buf, &func_name, &type_name, &msg);
        }
        _ => {}
    }

    0
}

#[cfg(feature = "python")]
#[pyfunction]
fn start_profiler_py(session_id: String) -> PyResult<()> {
    // Store session in thread-local storage
    ACTIVE_SESSION_ID.with(|cell| { *cell.borrow_mut() = Some(session_id.clone()); });
    
    // Store session globally for cross-thread access
    if let Ok(mut global_session) = GLOBAL_SESSION_ID.lock() {
        *global_session = Some(session_id);
    }
    
    // Enable profiling for the current thread
    unsafe { ffi::PyEval_SetProfile(Some(profiler_callback), ptr::null_mut()); }
    
    // Install thread creation hook to auto-enable profiling on new threads
    install_thread_hook();
    
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn stop_profiler_py() -> PyResult<()> {
    unsafe { ffi::PyEval_SetProfile(None, ptr::null_mut()); }
    ACTIVE_SESSION_ID.with(|cell| { *cell.borrow_mut() = None; });
    CALL_T0.with(|m| m.borrow_mut().clear());
    
    // Also clear global session
    if let Ok(mut global_session) = GLOBAL_SESSION_ID.lock() {
        *global_session = None;
    }
    
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn get_active_session_id_py() -> PyResult<Option<String>> {
    // First try thread-local storage
    let mut session_id = None;
    ACTIVE_SESSION_ID.with(|cell| {
        session_id = cell.borrow().clone();
    });
    
    // If no thread-local session, try global session (for worker threads)
    if session_id.is_none() {
        if let Ok(global_session) = GLOBAL_SESSION_ID.lock() {
            session_id = global_session.clone();
        }
    }
    
    Ok(session_id)
}

#[cfg(feature = "python")]
#[pyfunction]
fn suppress_profiler_enter_py() -> PyResult<()> {
    SUPPRESS_COUNT.with(|c| {
        let mut v = c.borrow_mut();
        *v = v.saturating_add(1);
    });
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn suppress_profiler_exit_py() -> PyResult<()> {
    SUPPRESS_COUNT.with(|c| {
        let mut v = c.borrow_mut();
        if *v > 0 { *v -= 1; }
    });
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn flush_events_to_file_py(path: String) -> PyResult<()> {
    exporter::write_events_to_file(&path);
    Ok(())
}

// Backwards-compatible alias for Python code expecting `flush_events_to_file`
#[cfg(feature = "python")]
#[pyfunction(name = "flush_events_to_file")]
fn flush_events_to_file_alias(path: String) -> PyResult<()> {
    exporter::write_events_to_file(&path);
    Ok(())
}

#[cfg(feature = "python")]
#[pymodule]
fn handit_core_native(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    exporter::init_collector();

    m.add_function(wrap_pyfunction!(start_session_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_call_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_call_with_args_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_return_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_return_with_preview_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_exception_py, m)?)?;

    m.add_function(wrap_pyfunction!(start_profiler_py, m)?)?;
    m.add_function(wrap_pyfunction!(stop_profiler_py, m)?)?;
    m.add_function(wrap_pyfunction!(get_active_session_id_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_http_request_py, m)?)?;
    m.add_function(wrap_pyfunction!(on_http_response_py, m)?)?;
    m.add_function(wrap_pyfunction!(suppress_profiler_enter_py, m)?)?;
    m.add_function(wrap_pyfunction!(suppress_profiler_exit_py, m)?)?;
    // expose flush to file
    m.add_function(wrap_pyfunction!(flush_events_to_file_py, m)?)?;
    m.add_function(wrap_pyfunction!(flush_events_to_file_alias, m)?)?;
    // also expose HTTP flush
    #[cfg(feature = "python")]
    {
        #[pyfunction]
        fn flush_events_http_py() -> PyResult<()> { exporter::flush_events_http(); Ok(()) }
        m.add_function(wrap_pyfunction!(flush_events_http_py, m)?)?;
    }

    // Expose HTTP config setter for Python configure()
    {
        #[pyfunction]
        fn set_http_config_py(endpoint: Option<String>, api_key: Option<String>) -> PyResult<()> {
            exporter::set_http_config(endpoint, api_key);
            Ok(())
        }
        m.add_function(wrap_pyfunction!(set_http_config_py, m)?)?;
    }

    Ok(())
}

#[cfg(not(feature = "python"))]
pub fn build_info() -> &'static str {
    "handit-py built without python feature; enable feature \"python\" to build the extension module"
}