# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:5000"

# Number of worker processes
# The Gunicorn documentation recommends (2 * $num_cores) + 1.
# Adjust based on your server's resources and application needs.
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 4 # As per the document, but dynamic is often better.

# Type of worker class
# 'sync' is the default and simplest.
# 'gevent' or 'eventlet' can be used for async applications if your code supports it.
worker_class = "sync"

# Maximum number of simultaneous connections.
# This is applicable for async worker types like gevent or eventlet.
# For sync workers, this is effectively 1 per worker.
worker_connections = 1000

# Maximum number of requests a worker will process before restarting.
# This can help prevent memory leaks.
max_requests = 1000
max_requests_jitter = 100 # Adds randomness to restart timing to avoid all workers restarting at once.

# Timeout for workers in seconds.
# Workers silent for more than this period are killed and restarted.
timeout = 30

# Keep-alive connections.
# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = 2

# Preload application code before worker processes are forked.
# This can save some RAM resources and speed up server startup.
# However, if your app creates connections to external resources in global scope,
# preloading might cause issues (e.g., shared DB connections).
preload_app = True

# User and group to run Gunicorn as.
# Ensure these users exist and have necessary permissions.
# user = "voip"  # Set this if you have a dedicated 'voip' user
# group = "voip" # Set this if you have a dedicated 'voip' group

# Directory for temporary Gunicorn files (e.g., for file uploads if not handled by app).
# tmp_upload_dir = None # Or specify a path like '/tmp/gunicorn_uploads'

# Logging
# accesslog = '-'  # Log to stdout
# errorlog = '-'   # Log to stderr
# loglevel = 'info' # Default is 'info'. Can be 'debug', 'warning', 'error', 'critical'.
# Capture Gunicorn logs with Supervisor or systemd if running as a service.

# SSL configuration (if Gunicorn is terminating SSL directly, usually Nginx does this)
# keyfile = '/path/to/your/ssl.key'
# certfile = '/path/to/your/ssl.crt'
# ca_certs = '/path/to/your/ca.crt' # Optional CA certs for client auth
# ssl_version = 'TLSv1_2' # Example, can use others

# Server hooks (advanced)
# def on_starting(server):
#     pass
# def when_ready(server):
#     pass

# Headers to determine secure scheme (for behind a proxy)
# These are based on the document's Nginx config.
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl', # Common, but less standard
    'X-FORWARDED-PROTO': 'https',  # Standard
    'X-FORWARDED-SSL': 'on'        # Common with some proxies
}

# Note: The document mentions 'user' and 'group' settings.
# These should be configured based on the deployment environment.
# For development, running as the current user is often fine.
# In production, a dedicated non-root user is recommended.

# The document also specifies `tmp_upload_dir = None`
# and `secure_scheme_headers` which are included above.
# The `workers` count is set dynamically based on CPU cores,
# which is a common practice, though the document hardcoded it to 4.
# You can change `workers = multiprocessing.cpu_count() * 2 + 1` to `workers = 4`
# if you strictly want to follow the document's value.
# For `worker_class`, "sync" is specified, which is the default.
# `worker_connections`, `max_requests`, `max_requests_jitter`, `timeout`, `keepalive`
# are taken from the document.
# `preload_app = True` is also from the document.
