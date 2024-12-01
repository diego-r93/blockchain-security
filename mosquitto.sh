#!/bin/sh

# Protects script from continuing with an error
set -eu -o pipefail

# Path to the passwd file
PASSWD_FILE="/mosquitto/config/passwd"

# Check if the file doesn't exist or is empty
if [ ! -s "$PASSWD_FILE" ]; then
    # Create or empty the passwd file
    > "$PASSWD_FILE"

    # Add the user and password
    mosquitto_passwd -b "$PASSWD_FILE" "${MQTT_USER_NAME}" "${MQTT_PASSWORD}"
fi

# Start Mosquitto
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
