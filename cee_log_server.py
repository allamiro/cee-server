import os
import sys
import signal
import logging
import logging.handlers
import json
import ssl
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from xml.etree.ElementTree import ParseError, fromstring
import configparser

# This script:
# - Reads settings from config.ini
# - Creates an HTTP server on port 8000 (default).
# - Optionally enables SSL based on config.
# - Expects to receive CEE audit events (JSON, XML, text) via PUT requests at /cee.
# - Logs events into separate files based on their type.
# - Validates JSON/XML; logs text as-is.
# - Gracefully handles Ctrl+C and SIGTERM, ensuring port reuse.

# If you see "Address already in use" errors after a Ctrl+C:
# 1. Check running processes: lsof -i :8000 or netstat -anp | grep 8000
# 2. Kill lingering processes: kill -9 <PID>

# Sample config.ini:
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
if not os.path.exists(config_path):
    print(f"No config file found at {config_path}. Please create one.", file=sys.stderr)
    sys.exit(1)

config.read(config_path)

LOG_DIR = config.get('server', 'log_dir', fallback='/Users/ghost/Desktop/GIT-PROJECTS/cee-server/')
SSL_ENABLED = config.getboolean('server', 'ssl', fallback=False)
SSL_VERIFY = config.getboolean('server', 'ssl_verify', fallback=False)
SSL_CA = config.get('server', 'ssl_ca', fallback='')
SSL_CERT = config.get('server', 'ssl_cert', fallback='')
SSL_KEY = config.get('server', 'ssl_key', fallback='')

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError as e:
    print(f"Failed to create log directory {LOG_DIR}: {e}", file=sys.stderr)
    sys.exit(1)

def setup_logger(log_type):
    log_file_path = os.path.join(LOG_DIR, f"cee_events_{log_type}.log")
    handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when='D', interval=1, backupCount=7, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_type)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

json_logger = setup_logger("json")
xml_logger = setup_logger("xml")
text_logger = setup_logger("text")

def is_valid_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def is_valid_xml(data):
    try:
        fromstring(data)
        return True
    except ParseError:
        return False

class CEERequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path != "/cee":
            self.send_error(404, "Endpoint not found")
            return

        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            self.send_error(400, "No data provided")
            return

        raw_data = self.rfile.read(length)
        event_str = raw_data.decode('utf-8', errors='replace')
        content_type = self.headers.get('Content-Type', '')

        if "application/json" in content_type:
            if is_valid_json(event_str):
                json_logger.info(event_str)
                log_type = "json"
            else:
                self.send_error(400, "Invalid JSON format.")
                return
        elif "application/xml" in content_type or "text/xml" in content_type:
            if is_valid_xml(event_str):
                xml_logger.info(event_str)
                log_type = "xml"
            else:
                self.send_error(400, "Invalid XML format.")
                return
        elif "text/plain" in content_type:
            text_logger.info(event_str)
            log_type = "text"
        else:
            self.send_error(400, "Unsupported content type. Use JSON, XML, or plain text.")
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"{log_type.upper()} log received and recorded".encode('utf-8'))

    def do_GET(self):
        if self.path == "/cee":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"CEE logging endpoint active")
        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        # Override to reduce console output noise
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(),
                                               self.log_date_time_string(),
                                               format%args))

def graceful_shutdown(signum, frame):
    print("Shutting down server...")
    httpd.shutdown()
    httpd.server_close()
    logging.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CEERequestHandler)
    # Allow immediate reuse of the port after the server stops
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # If SSL is enabled, wrap the server socket with SSL
    if SSL_ENABLED:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)
        if SSL_VERIFY:
            context.verify_mode = ssl.CERT_REQUIRED
            if SSL_CA:
                context.load_verify_locations(SSL_CA)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print("Secure CEE Log Server running on https://localhost:8000")
    else:
        print("CEE Log Server running on http://localhost:8000")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        httpd.server_close()
        logging.shutdown()
        print("Server shut down.")
