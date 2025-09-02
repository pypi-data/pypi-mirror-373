use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use serde_json::Value as JsonValue;
use std::collections::HashMap;
use std::sync::mpsc::{self, Sender};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeInfo {
    pub language: String,
    pub version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionStart {
    pub session_id: String,
    pub tag: Option<String>,
    pub ts_ns: u128,
    pub attrs: HashMap<String, String>,
    pub trace_id: Option<String>,
    pub span_id: Option<String>,
    pub runtime: RuntimeInfo,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CallEvent {
    pub session_id: String,
    pub func: String,
    pub module: String,
    pub file: String,
    pub line: u32,
    pub t0_ns: u128,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub args_preview: Option<JsonValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReturnEvent {
    pub session_id: String,
    pub func: String,
    pub t1_ns: u128,
    pub dt_ns: u128,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub locals_preview: Option<JsonValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExceptionEvent {
    pub session_id: String,
    pub func: String,
    pub ts_ns: u128,
    pub type_name: String,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HttpRequestEvent {
    pub session_id: String,
    pub method: String,
    pub url: String,
    pub t0_ns: u128,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<JsonValue>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bytes_out: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub request_body: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HttpResponseEvent {
    pub session_id: String,
    pub status: i32,
    pub t1_ns: u128,
    pub dt_ns: u128,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<JsonValue>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bytes_in: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response_body: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum Event {
    SessionStart(SessionStart),
    Call(CallEvent),
    Return(ReturnEvent),
    Exception(ExceptionEvent),
    HttpRequest(HttpRequestEvent),
    HttpResponse(HttpResponseEvent),
}

pub fn now_ns() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos()
}

pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

static GLOBAL_SENDER: Lazy<Mutex<Option<Sender<Event>>>> = Lazy::new(|| Mutex::new(None));

pub fn init_global(sender: Sender<Event>) {
    let mut guard = GLOBAL_SENDER.lock().unwrap();
    *guard = Some(sender);
}

fn emit(event: Event) {
    if let Some(tx) = GLOBAL_SENDER.lock().unwrap().as_ref() {
        let _ = tx.send(event);
    }
}

#[derive(Debug, Clone)]
pub struct SessionHandle {
    pub session_id: String,
}

pub fn start_session(tag: Option<String>, attrs: HashMap<String, String>, trace_id: Option<String>, span_id: Option<String>) -> SessionHandle {
    start_session_with_runtime(tag, attrs, trace_id, span_id, "python", &version())
}

pub fn start_session_with_runtime(
    tag: Option<String>, 
    attrs: HashMap<String, String>, 
    trace_id: Option<String>, 
    span_id: Option<String>,
    language: &str,
    version: &str,
) -> SessionHandle {
    let session_id = Uuid::new_v4().to_string();
    let start = SessionStart {
        session_id: session_id.clone(),
        tag,
        ts_ns: now_ns(),
        attrs,
        trace_id,
        span_id,
        runtime: RuntimeInfo { language: language.to_string(), version: version.to_string() },
    };
    emit(Event::SessionStart(start));
    SessionHandle { session_id }
}

pub fn end_session(_session: SessionHandle) {
    // Placeholder for future end event
}

pub fn on_call(session: &SessionHandle, func: &str, module: &str, file: &str, line: u32, t0_ns: u128) {
    emit(Event::Call(CallEvent {
        session_id: session.session_id.clone(),
        func: func.to_string(),
        module: module.to_string(),
        file: file.to_string(),
        line,
        t0_ns,
        args_preview: None,
    }));
}

pub fn on_return(session: &SessionHandle, func: &str, t1_ns: u128, dt_ns: u128) {
    emit(Event::Return(ReturnEvent {
        session_id: session.session_id.clone(),
        func: func.to_string(),
        t1_ns,
        dt_ns,
        locals_preview: None,
    }));
}

pub fn on_exception(session: &SessionHandle, func: &str, type_name: &str, message: &str) {
    emit(Event::Exception(ExceptionEvent {
        session_id: session.session_id.clone(),
        func: func.to_string(),
        ts_ns: now_ns(),
        type_name: type_name.to_string(),
        message: message.to_string(),
    }));
}

// Convenience FFI-friendly helpers operating on session_id directly
pub fn on_call_by_id(session_id: &str, func: &str, module: &str, file: &str, line: u32, t0_ns: u128) {
    emit(Event::Call(CallEvent {
        session_id: session_id.to_string(),
        func: func.to_string(),
        module: module.to_string(),
        file: file.to_string(),
        line,
        t0_ns,
        args_preview: None,
    }));
}

pub fn on_return_by_id(session_id: &str, func: &str, t1_ns: u128, dt_ns: u128) {
    emit(Event::Return(ReturnEvent {
        session_id: session_id.to_string(),
        func: func.to_string(),
        t1_ns,
        dt_ns,
        locals_preview: None,
    }));
}

pub fn on_exception_by_id(session_id: &str, func: &str, type_name: &str, message: &str) {
    emit(Event::Exception(ExceptionEvent {
        session_id: session_id.to_string(),
        func: func.to_string(),
        ts_ns: now_ns(),
        type_name: type_name.to_string(),
        message: message.to_string(),
    }));
}

pub fn on_call_with_args_preview_by_id(
    session_id: &str,
    func: &str,
    module: &str,
    file: &str,
    line: u32,
    t0_ns: u128,
    args_preview: JsonValue,
) {
    emit(Event::Call(CallEvent {
        session_id: session_id.to_string(),
        func: func.to_string(),
        module: module.to_string(),
        file: file.to_string(),
        line,
        t0_ns,
        args_preview: Some(args_preview),
    }));
}

pub fn on_return_with_locals_preview_by_id(
    session_id: &str,
    func: &str,
    t1_ns: u128,
    dt_ns: u128,
    locals_preview: JsonValue,
) {
    emit(Event::Return(ReturnEvent {
        session_id: session_id.to_string(),
        func: func.to_string(),
        t1_ns,
        dt_ns,
        locals_preview: Some(locals_preview),
    }));
}

pub fn http_request_by_id(session_id: &str, method: &str, url: &str, t0_ns: u128, headers: Option<JsonValue>, bytes_out: Option<u64>, request_body: Option<String>) {
    emit(Event::HttpRequest(HttpRequestEvent {
        session_id: session_id.to_string(),
        method: method.to_string(),
        url: url.to_string(),
        t0_ns,
        headers,
        bytes_out,
        request_body,
    }));
}

pub fn http_response_by_id(session_id: &str, status: i32, t1_ns: u128, dt_ns: u128, headers: Option<JsonValue>, bytes_in: Option<u64>, error: Option<String>, response_body: Option<String>) {
    emit(Event::HttpResponse(HttpResponseEvent {
        session_id: session_id.to_string(),
        status,
        t1_ns,
        dt_ns,
        headers,
        bytes_in,
        error,
        response_body,
    }));
}