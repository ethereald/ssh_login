#!/bin/bash

# Base64 encoded password (replace this with your actual encoded password)
ENCODED_PASS="UUE7cEAzMy4="  # This is just an example
REMOTE_USER="qa"

# Check if IP address is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <ip_address>"
    exit 1
fi

REMOTE_HOST=$1
# Decode the password
REMOTE_PASS=$(echo $ENCODED_PASS | base64 -d)

# Debug password (length only, not content)
PASS_LENGTH=$(echo -n "$REMOTE_PASS" | wc -c)
echo "Debug: Password length: $PASS_LENGTH"

# Export variables for expect
export REMOTE_USER
export REMOTE_HOST
export REMOTE_PASS

# Use expect to handle SSH login
/usr/bin/expect -f - <<EOF
# Enable expect internal debugging
exp_internal 1
set timeout 30

# Get environment variables
set remote_user \$env(REMOTE_USER)
set remote_host \$env(REMOTE_HOST)
set remote_pass \$env(REMOTE_PASS)

# Debug password length (not content)
send_user "Debug: Password length: [string length \$remote_pass]\n"

# Debug output
send_user "Debug: Connecting as \$remote_user to \$remote_host\n"

# Keep logging enabled for debugging
log_user 1

send_user "\nAttempting SSH connection...\n"
spawn ssh "\$remote_user@\$remote_host"

# Wait for password prompt
expect {
    -re "yes/no|fingerprint" {
        send "yes\r"
        exp_continue
    }
    "assword:" {
        send "\$remote_pass\r"
    }
    timeout {
        send_user "\nError: Connection timeout\n"
        exit 1
    }
    eof {
        send_user "\nError: Connection failed\n"
        exit 1
    }
}

# Wait for successful login or error
expect {
    -re "(Microsoft Windows|Windows|\[Ww\]indows)" {
        send_user "Windows login detected\n"
        exp_continue
    }
    -re "\[Cc\]:\\\\.*>" {
        send_user "Windows prompt found\n"
    }
    -re ".*@.*>" {
        send_user "Windows prompt found\n"
    }
    "Permission denied" {
        send_user "\nError: Invalid password\n"
        exit 1
    }
    "Connection refused" {
        send_user "\nError: Connection refused\n"
        exit 1
    }
    timeout {
        send_user "\nError: Login timeout\n"
        exit 1
    }
    eof {
        send_user "\nError: Connection closed\n"
        exit 1
    }
}

# Turn off debugging
exp_internal 0

# Enter interactive mode
interact
    -re "Connection refused" {
        send_user "\nError: Connection refused - Please check if the host is available and SSH is running\n"
        exit 1
    }
    -re "Permission denied" {
        send_user "\nError: Invalid password\n"
        exit 1
    }
    eof {
        send_user "\nError: Connection failed\n"
        exit 1
    }
    timeout {
        send_user "\nError: Connection timeout\n"
        exit 1
    }
}

# We should never reach this point
exit 1
EOF
