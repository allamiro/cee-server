#!/usr/bin/bash
# This script creates a systemd service file for the CEE log server, enables it,
# and starts it. It assumes that:
# 1) The cee_log_server.py script is placed in /usr/local/bin/cee_log_server.py
# 2) Python 3 is available at /usr/bin/python3
# 3) You have root or sudo privileges

SERVICE_NAME="cee-server"
SERVICE_FILE="/usr/lib/systemd/system/${SERVICE_NAME}.service"
SCRIPT_PATH="/usr/local/bin/cee_log_server.py"
PYTHON_PATH="/usr/bin/python3"
LOG_DIR="/var/log/cee-server"

# Ensure the Python script is present
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: $SCRIPT_PATH not found. Please place cee_log_server.py in /usr/local/bin/"
    exit 1
fi

# Ensure the log directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory at $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown nobody:nobody "$LOG_DIR"
    sudo chmod 750 "$LOG_DIR"
fi

# Create the systemd service unit file
cat <<EOF | sudo tee $SERVICE_FILE > /dev/null
[Unit]
Description=CEE Log Server
After=network.target

[Service]
Type=simple
ExecStart=${PYTHON_PATH} ${SCRIPT_PATH}
Restart=on-failure
User=nobody
Group=nobody
WorkingDirectory=/usr/local/bin
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set permissions on the service file
sudo chmod 644 $SERVICE_FILE

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable the service so it starts on boot
sudo systemctl enable ${SERVICE_NAME}.service

# Start the service now
sudo systemctl start ${SERVICE_NAME}.service

# Show service status
sudo systemctl status ${SERVICE_NAME}.service
