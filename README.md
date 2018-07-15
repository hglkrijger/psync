# psync
Tools for PiWiGo

## Installation

```bash
git clone https://github.com/hglkrijger/psync.git
cd psync
pip3 install -r requirements.txt
python3 setup.py install
```

### Service management

```bash
less /usr/sbin/psync
less /lib/systemd/system/psync.service
systemctl daemon-reload
systemctl enable psync.service
systemctl start psync.service
systemctl stop psync.service
systemctl disable psync.service
```

## Usage

### Help

```bash
python3 psync --help
```

### Logging levels
```bat
SET LOGLEVEL=DEBUG
```
```bash
LOGLEVEL='DEBUG'
```

### Generating a OneDrive session

This requires a browser with JavaScript support.

```bash
python3 psync --new-session secrets/secrets.ini
```

### Refreshing an existing session

Ensure the same version of Python is used to generate and refresh the session.

```bash
python3 psync --refresh-session secrets/secrets.ini
```
or
```bash
python3 psync --refresh-session app_id
```

### Running filename cleanup

```bash
python psync --clean folder
``` 