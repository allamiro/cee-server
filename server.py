from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os
import json
import xml.etree.ElementTree as ET
import threading
import time
import shutil

# Directory to save logs
LOG_DIR = "cee_logs"
ROTATION_INTERVAL = 60 * 60 * 24  # Rotate logs daily

def rotate_logs():
    while True:
        time.sleep(ROTATION_INTERVAL)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{LOG_DIR}_{timestamp}.zip"
        shutil.make_archive(LOG_DIR, 'zip', LOG_DIR)
        shutil.move(f"{LOG_DIR}.zip", archive_name)
        shutil.rmtree(LOG_DIR)
        os.makedirs(LOG_DIR, exist_ok=True)

class CEELogHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        body = self.rfile.read(content_length)
        
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        try:
            if content_type == "application/cee+json":
                data = json.loads(body)
                file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
                with open(os.path.join(LOG_DIR, file_name), "w") as f:
                    json.dump(data, f, indent=4)

            elif content_type == "application/cee+xml":
                root = ET.fromstring(body)
                file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".xml"
                with open(os.path.join(LOG_DIR, file_name), "wb") as f:
                    f.write(body)

            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Unsupported Content-Type")
                return

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Log received successfully")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error processing log: {str(e)}".encode())

    def log_message(self, format, *args):
        # Suppress default logging
        return

def run_server():
    server = HTTPServer(("", 8000), CEELogHandler)
    print("Server started on port 8000...")
    server.serve_forever()

if __name__ == "__main__":
    # Start the log rotation thread
    threading.Thread(target=rotate_logs, daemon=True).start()

    # Start the server
    run_server()
