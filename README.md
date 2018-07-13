# psync
Tools for PiWiGo

## Installation

Replace `python` and `pip` with `python3` and `pip3` as appropriate. 

```bash
git clone https://github.com/hglkrijger/psync.git
cd psync
sudo pip install -r requirements.txt
sudo python setup.py install
```

## Usage

### Help

```bash
python psync --help
```

### Generating a OneDrive session

This requires a browser with JavaScript support.

```bash
sudo python psync --new-session secrets/secrets.ini
```

### Loading an existing session

Ensure the same version of Python is used to generate and load the session.

```bash
python psync --load-session secrets/secrets.ini
```
or
```bash
python psync --load-session app_id
```

### Running filename cleanup

```bash
python psync --clean folder
``` 