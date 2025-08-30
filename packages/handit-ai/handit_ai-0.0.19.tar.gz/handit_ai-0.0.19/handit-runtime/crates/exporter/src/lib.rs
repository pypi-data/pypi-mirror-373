use handit_core::{init_global, Event};
use once_cell::sync::Lazy;
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::sync::mpsc::{self, Receiver, RecvTimeoutError};
use std::sync::Mutex;
use std::thread;
use std::time::{Duration, Instant};
use std::env;

// In-memory batch buffer as serialized JSONL lines; drained to file periodically to bound memory
static EVENTS: Lazy<Mutex<Vec<String>>> = Lazy::new(|| Mutex::new(Vec::new()));
static BUFFER_BYTES: Lazy<Mutex<usize>> = Lazy::new(|| Mutex::new(0usize));
static HTTP_ENDPOINT_OVERRIDE: Lazy<Mutex<Option<String>>> = Lazy::new(|| Mutex::new(None));
static HTTP_API_KEY_OVERRIDE: Lazy<Mutex<Option<String>>> = Lazy::new(|| Mutex::new(None));

#[derive(Clone)]
struct ExportConfig {
    output_path: String,
    flush_every_events: usize,
    flush_every_ms: u64,
    max_buffer_events: usize,
    max_buffer_bytes: usize,
    http_endpoint: Option<String>,
    http_api_key: Option<String>,
    spool_dir: String,
}

static CONFIG: Lazy<ExportConfig> = Lazy::new(|| ExportConfig {
    output_path: env::var("HANDIT_OUTPUT_FILE").unwrap_or_else(|_| "./handit_events.jsonl".to_string()),
    flush_every_events: env::var("HANDIT_FLUSH_EVERY_EVENTS").ok().and_then(|v| v.parse().ok()).unwrap_or(200),
    flush_every_ms: env::var("HANDIT_FLUSH_EVERY_MS").ok().and_then(|v| v.parse().ok()).unwrap_or(1000),
    max_buffer_events: env::var("HANDIT_MAX_BUFFER_EVENTS").ok().and_then(|v| v.parse().ok()).unwrap_or(10_000),
    // 8 MiB default cap on buffered bytes
    max_buffer_bytes: env::var("HANDIT_MAX_BUFFER_BYTES").ok().and_then(|v| v.parse().ok()).unwrap_or(8 * 1024 * 1024),
    http_endpoint: Some(env::var("HANDIT_ENDPOINT").unwrap_or_else(|_| "https://handit-api-oss-299768392189.us-central1.run.app/api/ingest/events".to_string())),
    http_api_key: env::var("HANDIT_API_KEY").ok(),
    spool_dir: env::var("HANDIT_SPOOL_DIR").unwrap_or_else(|_| "./handit_spool".to_string()),
});

pub fn init_collector() {
    let (tx, rx) = mpsc::channel::<Event>();
    init_global(tx);
    spawn_collector_worker(rx);
}

fn spawn_collector_worker(rx: Receiver<Event>) {
    thread::spawn(move || {
        let cfg = CONFIG.clone();
        let mut last_flush = Instant::now();
        let mut rate_window_start = Instant::now();
        let mut rate_window_events: usize = 0;
        loop {
            match rx.recv_timeout(Duration::from_millis(cfg.flush_every_ms)) {
                Ok(ev) => {
                    // Serialize once to track exact bytes and avoid re-serialization on flush
                    let line = match serde_json::to_string(&ev) {
                        Ok(mut s) => { s.push('\n'); s }
                        Err(_) => {
                            // If serialization fails, skip this event but keep going
                            String::new()
                        }
                    };
                    let line_len = line.len();
                    let mut should_flush = false;
                    if line_len > 0 {
                        if let Ok(mut vec) = EVENTS.lock() {
                            vec.push(line);
                            // update bytes
                            if let Ok(mut b) = BUFFER_BYTES.lock() { *b += line_len; }
                            // hard caps
                            if vec.len() >= cfg.flush_every_events || vec.len() >= cfg.max_buffer_events {
                                should_flush = true;
                            }
                            if let Ok(b) = BUFFER_BYTES.lock() {
                                if *b >= cfg.max_buffer_bytes { should_flush = true; }
                            }
                        }
                    }
                    // Update rate and proactively flush if we risk hitting caps before next interval
                    rate_window_events += 1;
                    let rate_elapsed = rate_window_start.elapsed();
                    if rate_elapsed >= Duration::from_millis(250) { // small window
                        let eps = (rate_window_events as f64) / (rate_elapsed.as_secs_f64().max(1e-6));
                        if eps > 0.0 {
                            if let Ok(vec) = EVENTS.lock() {
                                let remaining_events = cfg.max_buffer_events.saturating_sub(vec.len());
                                let time_to_cap = (remaining_events as f64) / eps; // seconds
                                if time_to_cap < (cfg.flush_every_ms as f64 / 1000.0) {
                                    should_flush = true;
                                }
                            }
                        }
                        rate_window_start = Instant::now();
                        rate_window_events = 0;
                    }
                    if should_flush || last_flush.elapsed() >= Duration::from_millis(cfg.flush_every_ms) {
                        // Try network first (non-blocking wrt producer)
                        #[cfg(feature = "http")] {
                            flush_buffer_http();
                        }
                        // Always also flush to file as durable spool
                        flush_buffer_to_file(&cfg.output_path);
                        last_flush = Instant::now();
                    }
                }
                Err(RecvTimeoutError::Timeout) => {
                    // Periodic time-based flush
                    #[cfg(feature = "http")] {
                        flush_buffer_http();
                    }
                    flush_buffer_to_file(&cfg.output_path);
                    last_flush = Instant::now();
                }
                Err(RecvTimeoutError::Disconnected) => {
                    // Final flush and exit
                    #[cfg(feature = "http")] {
                        flush_buffer_http();
                    }
                    flush_buffer_to_file(&cfg.output_path);
                    break;
                }
            }
        }
    });
}

fn flush_buffer_to_file(path: &str) {
    // Drain to minimize time under lock and avoid duplicate writes
    let drained: Vec<String> = {
        let mut guard = match EVENTS.lock() { Ok(g) => g, Err(poisoned) => poisoned.into_inner() };
        if guard.is_empty() { return; }
        let drained = guard.drain(..).collect::<Vec<_>>();
        // reset byte counter
        if let Ok(mut b) = BUFFER_BYTES.lock() { *b = 0; }
        drained
    };
    if drained.is_empty() { return; }
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(path) {
        for line in drained.iter() { let _ = file.write_all(line.as_bytes()); }
        let _ = file.flush();
    } else {
        // If we cannot open the file, requeue the events so we don't lose them
        let bytes_to_restore: usize = drained.iter().map(|s| s.len()).sum();
        if let Ok(mut guard) = EVENTS.lock() { guard.extend(drained.into_iter()); }
        if let Ok(mut b) = BUFFER_BYTES.lock() { *b += bytes_to_restore; }
    }
}

// Public API to force a flush to a specific path (e.g., at process exit)
pub fn write_events_to_file(path: &str) {
    flush_buffer_to_file(path);
}

// Public API to force an HTTP flush (best-effort)
pub fn flush_events_http() {
    #[cfg(feature = "http")]
    {
        flush_buffer_http();
    }
}

#[cfg(feature = "http")]
fn http_client() -> reqwest::blocking::Client {
    reqwest::blocking::Client::builder()
        .gzip(true)
        .pool_idle_timeout(Duration::from_secs(30))
        .pool_max_idle_per_host(2)
        .build()
        .unwrap()
}

#[cfg(feature = "http")]
fn try_send_batch(client: &reqwest::blocking::Client, endpoint: &str, api_key: Option<&str>, lines: &[String]) {
    if lines.is_empty() { return; }
    // Concatenate and compress using gzip
    let payload = lines.join("");
    use flate2::write::GzEncoder;
    use flate2::Compression;
    let mut encoder = GzEncoder::new(Vec::new(), Compression::fast());
    let _ = std::io::Write::write_all(&mut encoder, payload.as_bytes());
    let compressed = encoder.finish().unwrap_or_default();
    let mut req = client.post(endpoint)
        .header("Content-Type", "application/jsonl")
        .header("Content-Encoding", "gzip")
        .body(compressed);
    if let Some(k) = api_key { req = req.header("Authorization", format!("Bearer {}", k)); }
    let _ = req.send();
}

#[cfg(feature = "http")]
fn flush_buffer_http() {
    let cfg = &*CONFIG;
    let endpoint = {
        let over = HTTP_ENDPOINT_OVERRIDE.lock().ok().and_then(|g| g.clone());
        over.or_else(|| cfg.http_endpoint.clone())
    };
    let endpoint = match endpoint { Some(e) => e, None => return };
    let api_key_override = HTTP_API_KEY_OVERRIDE.lock().ok().and_then(|g| g.clone());
    // clone current buffer without draining; file flush handles durability
    let snapshot: Vec<String> = {
        let guard = match EVENTS.lock() { Ok(g) => g, Err(poisoned) => poisoned.into_inner() };
        if guard.is_empty() { return; }
        guard.clone()
    };
    let client = http_client();
    // chunk into ~512KB batches
    let mut batch: Vec<String> = Vec::new();
    let mut batch_bytes = 0usize;
    for line in snapshot.into_iter() {
        let len = line.len();
        if batch_bytes + len > 512_000 && !batch.is_empty() {
            let api = api_key_override.as_deref().or(cfg.http_api_key.as_deref());
            try_send_batch(&client, &endpoint, api, &batch);
            batch.clear();
            batch_bytes = 0;
        }
        batch_bytes += len;
        batch.push(line);
    }
    if !batch.is_empty() {
        let api = api_key_override.as_deref().or(cfg.http_api_key.as_deref());
        try_send_batch(&client, &endpoint, api, &batch);
    }
}

pub fn set_http_config(endpoint: Option<String>, api_key: Option<String>) {
    if let Ok(mut e) = HTTP_ENDPOINT_OVERRIDE.lock() { *e = endpoint; }
    if let Ok(mut k) = HTTP_API_KEY_OVERRIDE.lock() { *k = api_key; }
}