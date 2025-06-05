# SSH Login Tool (li)

A command-line tool for automated SSH login to Windows servers with password authentication.

## Features

- Automated SSH login with password authentication
- Base64 encoded password storage
- Configuration stored in `~/.config/li/config.properties`
- Clean and simple interface
- No password echo during login
- Proper handling of Windows prompts and banners

## Installation

1. Build from source:
```bash
cd ssh_login
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pyinstaller login.spec
```

2. Install the executable:
```bash
sudo mv dist/li /usr/local/bin/
```

## Configuration

The tool stores its configuration in `~/.config/li/config.properties` with the following format:
```properties
ENCODED_PASS=<base64_encoded_password>
REMOTE_USER=<username>
```

The config file will be created automatically on first run with default values.

## Usage

```bash
li <ip_address>
```

Example:
```bash
li 172.18.101.13
```

## Security

- Passwords are stored base64 encoded in the config file
- No password echoing during login
- Configuration file is stored in user's home directory with appropriate permissions
