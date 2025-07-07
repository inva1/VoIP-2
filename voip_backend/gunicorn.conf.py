# Gunicorn configuration file for VoIP Business Solution Backend
# Based on VoIP Business Solution: Enhanced Deployment Guide (Version 2.0)

import multiprocessing
import os

# Network settings
# Bind to 0.0.0.0 to be accessible externally (e.g., from Nginx proxy)
# The port 5000 is the default Flask development port, also used here for Gunicorn.
bind = os.environ.get('GUNICORN_BIND', "0.0.0.0:5000")

# Worker processes
# The document suggests 4 workers. A common rule of thumb is (2 * CPU_CORES) + 1.
# Adjust based on server resources and application characteristics.
workers = int(os.environ.get('GUNICORN_WORKERS', 4))

# Worker class
# 'sync' is the default and simplest.
# For I/O bound applications, consider 'gevent' or 'eventlet' if dependencies are compatible.
# The document specifies 'sync'.
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', "sync")

# Maximum number of simultaneous connections.
# Only applicable for async worker types (e.g., gevent, eventlet).
# For sync workers, this is effectively 1 per worker.
# The document specifies 1000, which is relevant if switching to async.
worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', 1000))

# Maximum number of requests a worker will process before restarting.
# Helps prevent memory leaks from affecting long-running workers.
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))

# Jitter to add to max_requests to prevent all workers restarting simultaneously.
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 100))

# Worker timeout (in seconds).
# Workers silent for more than this many seconds are killed and restarted.
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))

# Keep-alive connections.
# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 2))

# Preload application code before forking worker processes.
# Can save some RAM and speed up worker startup, but may have issues
# if app components are not fork-safe (e.g., some DB connections).
preload_app = os.environ.get('GUNICORN_PRELOAD_APP', 'True').lower() == 'true'

# User and group to run Gunicorn as.
# Should be a non-privileged user.
# The document specifies 'voip'. Ensure this user/group exists on the server.
user = os.environ.get('GUNICORN_USER', "voip")
group = os.environ.get('GUNICORN_GROUP', "voip")

# Temporary directory for Gunicorn to store data (e.g., for file uploads if not handled by app).
# Document specifies None, meaning Gunicorn won't use a specific tmp_upload_dir.
# If your application handles large file uploads directly through Gunicorn (less common with Flask),
# you might configure this.
# tmp_upload_dir = None

# SSL configuration (if Gunicorn terminates SSL directly, not recommended if behind Nginx)
# keyfile = os.environ.get('GUNICORN_KEYFILE', None)
# certfile = os.environ.get('GUNICORN_CERTFILE', None)
# ssl_version = 'TLSv1_2' # Example

# Logging
# accesslog = '-' # Log to stdout
# errorlog = '-'  # Log to stderr
# loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')
# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# These are typically handled by Supervisor or systemd, which captures stdout/stderr.
# The supervisor config in the doc redirects stdout to a file.

# Process naming
# proc_name = 'voip-backend'

# Server hooks (advanced)
# def on_starting(server):
#     pass
# def on_reload(server):
#     pass

# Secure scheme headers
# Important if Gunicorn is behind a proxy like Nginx that terminates SSL.
# Tells the application that requests are HTTPS even if Gunicorn receives HTTP from proxy.
# The document specifies these headers.
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on',
}

# Check configuration (Gunicorn will do this on startup)
# You can run `gunicorn --check-config gunicorn.conf.py myapp:app`

# Note: The application entry point (e.g., 'run:app' or 'wsgi:app') is specified
# in the Supervisor command, not directly in this Gunicorn config file.
# command=/opt/voip-backend/venv/bin/gunicorn -c gunicorn.conf.py run:app
# This means this config file will be loaded by that command.
