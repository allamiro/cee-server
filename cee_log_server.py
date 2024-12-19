import os
import sys
import logging
import logging.handlers
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# References:
# - Python's http.server module documentation: https://docs.python.org/3/library/http.server.html
# - CEE log formats and structure: MITRE CEE Specification (https://cee.mitre.org)
# - Common Event Enabler (CEE) auditing integration guidance from Dell EMC documentation (e.g., Dell EMC Common Event Enabler 6.6)
#   [No direct code examples; documentation available publicly from Dell/EMC and MITRE]
#
# Note: According to Dell EMC documentation, CEE forwards events via HTTP PUT operations to URIs like http://host:port/cee
#       For Isilon/PowerScale integration, one might configure the CEE URI on the cluster as: http://<this_server>:8000/cee
#
# This script:
# - Creates an HTTP server on port 8000.
# - Expects to receive CEE audit events (JSON or XML) via HTTP PUT requests at /cee endpoint.
# - Writes incoming audit event data to rotating log files stored in /data/isilon-cee/.
# - Uses only built-in libraries (no Flask), relying on http.server and standard logging.
# - Rotates logs daily, keeping 7 days of logs as a simple "best practice" example.
# - This code can be run directly (e.g., `python3 cee_log_server.py`), and the Isilon or CEE forwarder can be configured to send logs here.

# Ensure the directory for storing logs exists
LOG_DIR = "/var/log/cee-server/"

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError as e:
    print(f"Failed to create log directory {LOG_DIR}: {e}", file=sys.stderr)
    sys.exit(1)

# Set up a rotating log handler (daily rotation, keep 7 days)
log_file_path = os.path.join(LOG_DIR, "cee_events.log")
handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when='D', interval=1, backupCount=7, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("CEELogger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class CEERequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        # We expect requests to /cee according to Isilon documentation
        if parsed_path.path != "/cee":
            self.send_error(404, "Endpoint not found")
            return

        # Read content length
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            self.send_error(400, "No data provided")
            return

        # Read the raw body (this may be JSON or XML as per CEE spec)
        raw_data = self.rfile.read(length)

        # Log the event data
        # Just store as-is. If needed, additional validation of JSON/XML could be implemented.
        event_str = raw_data.decode('utf-8', errors='replace')
        logger.info(event_str)

        # Respond with 200 OK
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        if self.path == "/cee":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"CEE logging endpoint active")
        else:
            self.send_error(404, "Endpoint not found")

    # Disable logging of every request to stderr, or redirect it
    def log_message(self, format, *args):
        # To reduce console noise, redirect server logs to a logger if desired:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(),
                                               self.log_date_time_string(),
                                               format%args))

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CEERequestHandler)
    try: 
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
        
