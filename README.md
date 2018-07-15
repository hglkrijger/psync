# psync
Tools for PiWiGo

## Installation

```bash
git clone https://github.com/hglkrijger/psync.git
cd psync
pip3 install -r requirements.txt
[add secrets to psync.conf, see below]
python3 setup.py install
```

## Configuration

To sync with OneDrive, update `psync.conf` with the following structure:

```yml
[secrets]
client_id: application_id
client_secret: secret
redirect_uri: uri
``` 

These values should be obtained by registering an application at [https://apps.dev.microsoft.com](https://apps.dev.microsoft.com). 

More information at [https://developer.microsoft.com/en-us/graph/quick-start](https://developer.microsoft.com/en-us/graph/quick-start).

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
```bash
LOGLEVEL='DEBUG'
```

### Generating a OneDrive session

This requires a browser with JavaScript support.

```bash
python3 psync --new-session
```

### Refreshing an existing session

Ensure the same version of Python is used to generate and refresh the session.

```bash
python3 psync --refresh-session
```

### Syncing with OneDrive

Ensure the configuration values are set appropriately.

```bash
python3 psync --sync
```

### Running filename cleanup

```bash
python psync --clean folder
``` 