# psync
Tools for PiWiGo

## Installation

```bash
git clone git@github.com:hglkrijger/psync.git
cd psync
pip install -r requirements.txt
python setup.py install
```

## Usage

### Help

```bash
python psync --help
```

### Generating a OneDrive session

```bash
python psync --new-session secrets\secrets.ini
```

### Running filename cleanup

```bash
python psync --clean folder
``` 