# psync
Tools for PiWiGo

## Installation

```bash
git clone git@github.com:hglkrijger/psync.git
cd psync
pip install -r requirements.txt
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

### Running filename cleanup

```bash
python psync --clean folder
``` 