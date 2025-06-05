#!/usr/bin/env python3
import sys
import base64
import pexpect
import argparse
import os
from pathlib import Path

def read_config():
    # Use XDG_CONFIG_HOME if set, otherwise default to ~/.config
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    config_dir = config_home / 'li'
    config_path = config_dir / 'config.properties'
    config = {}
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write('ENCODED_PASS=UUE7cEAzMy4=\n')
            f.write('REMOTE_USER=qa\n')
    
    # Read config
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

def main():
    # Read configuration
    config = read_config()
    ENCODED_PASS = config.get('ENCODED_PASS', '')
    REMOTE_USER = config.get('REMOTE_USER', '')

    if not ENCODED_PASS or not REMOTE_USER:
        print("Error: Missing required configuration in config.properties")
        return

    parser = argparse.ArgumentParser(description='SSH login to Windows server')
    parser.add_argument('ip_address', help='IP address of the Windows server')
    args = parser.parse_args()

    # Decode the password
    remote_pass = base64.b64decode(ENCODED_PASS).decode('utf-8')

    # Spawn SSH process
    child = pexpect.spawn(f'ssh {REMOTE_USER}@{args.ip_address}')
    # Enable logging for connection phase
    child.logfile = sys.stdout.buffer

    connected = False
    while not connected:
        try:
            i = child.expect([
                'yes/no',                            # SSH first time connection
                'assword:',                          # Password prompt
                '(Microsoft Windows|Windows)',        # Windows login banner
                r'([Cc]:\\.*>|.*@.*>)',             # Windows prompt
                'Connection refused',                # Connection error
                'Permission denied',                 # Auth error
                pexpect.EOF,                         # Connection closed
                pexpect.TIMEOUT                      # Timeout
            ], timeout=30)

            if i == 0:  # SSH first time connection
                child.sendline('yes')
            elif i == 1:  # Password prompt
                # Temporarily disable logging while sending password
                old_logfile = child.logfile
                child.logfile = None
                child.sendline(remote_pass)
                child.logfile = old_logfile
            elif i == 2:  # Windows login banner
                pass  # Just continue without printing anything
            elif i == 3:  # Windows prompt found
                # Disable logging before entering interactive mode
                child.logfile = None
                connected = True
            elif i == 4:  # Connection refused
                print("\nError: Connection refused - Please check if the host is available and SSH is running")
                return
            elif i == 5:  # Permission denied
                print("\nError: Invalid password")
                return
            elif i == 6:  # EOF
                print("\nError: Connection failed")
                return
            elif i == 7:  # Timeout
                print("\nError: Connection timeout")
                return

        except Exception as e:
            print(f"\nError: {str(e)}")
            return

    # Successfully connected, switch to interactive mode
    try:
        child.interact()
    except Exception as e:
        print(f"\nConnection terminated: {str(e)}")
    finally:
        if child.isalive():
            child.close()

if __name__ == '__main__':
    main()
