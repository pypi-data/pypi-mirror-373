ClickUp HTTP Logging Debug Tools
=================================

This folder contains tools for debugging HTTP requests and responses made by the ClickUp toolkit.

## Files

- http_logging.py       - Core HTTP logging utilities
- http_log_viewer.html  - Interactive web viewer for HTTP logs
- http.jsonl            - Log file (generated when logging is enabled)

## Usage

### 1. Enable HTTP Logging

Set the environment variable to enable logging:

```bash
export CLICKUP_HTTP_LOG=1
```

### 2. Run Your ClickUp Tools

Execute any ClickUp toolkit functionality. HTTP requests and responses will be logged to `http.jsonl`.

### 3. View Logs in Browser

Since the HTML viewer needs to access local files, you must serve it over HTTP (not file://).

Start a local HTTP server in this directory:

```bash
cd toolkits/clickup/arcade_clickup/debug_tools
python3 -m http.server 8000
```

Then open in your browser:
http://localhost:8000/http_log_viewer.html

### 4. Disable Logging (Important!)

Always disable logging when done:

```bash
unset CLICKUP_HTTP_LOG
```

## Configuration Options

Environment variables for customization:

- CLICKUP_HTTP_LOG=1              - Enable logging (default: disabled)
- CLICKUP_HTTP_LOG_FILE=path      - Custom log file path (default: debug_tools/http.jsonl)
- CLICKUP_HTTP_LOG_MAX_BODY=2048  - Max bytes to log from request/response bodies
- CLICKUP_HTTP_LOG_REDACT=headers - Comma-separated headers to redact (default: auth headers)

## Log Viewer Features

The HTML viewer provides:
- Real-time log updates
- Request filtering by URL pattern or HTTP method

## Security Notes

- Authorization headers are automatically redacted
- Large request/response bodies are truncated
- The pre-commit hook ensures logging is disabled by default
- Never commit logs to version control (http.jsonl is in .gitignore)

## Troubleshooting

**CORS Error**: If you see a CORS policy error, make sure you're accessing the viewer via
http://localhost (not file://) and that you've started the HTTP server.

**No logs appearing**: Verify CLICKUP_HTTP_LOG=1 is set and that you're making actual
ClickUp API calls through the toolkit.

**Browser refresh not showing new logs**: The viewer auto-refreshes every 2 seconds, but you
can manually refresh the page or use the "Start/Stop" button to restart log polling.
