# commons-cli

Terminal-based chat client for Commons with real-time messaging support.

**IF YOU ARE LOOKING FOR THE API IT IS AT [https://github.com/WheeledCord/commons-api](https://github.com/WheeledCord/commons-api)!!!**

## Installation

### From PyPI (recommended)
```bash
pip install commons-cli
```

Then run:
```bash
commons-cli
# or
commons
```

### From Source
```bash
git clone <repo-url>
cd commons-cli
pip install -e .
```

## Development

### Local Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run from source:
```bash
python main.py
```

### Publishing to PyPI

1. Build the package:
```bash
./build_and_test.sh
```

2. Upload to PyPI:
```bash
twine upload dist/*
```

## Platform Support

- **Linux**: Full support
- **macOS**: Full support  
- **Windows**: Supported (use Windows Terminal or PowerShell for best experience)
