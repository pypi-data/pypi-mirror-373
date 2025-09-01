# Coco-Pack Python (Coco-PyPack)

This package contains Python utilities for Jupyter notebooks and development workflows.

## Installation & Uninstallation

### Installation

Basic installation (Python only):
```bash
pip install coco-pack
```

Full installation (with shell utilities):
```bash
pip install "coco-pack[shell]"
```

### Uninstallation

```bash
pip uninstall coco-pack
```

After uninstallation, remember to:
1. Remove any cocopack-related lines from your .bashrc or .zshrc
2. Clean up any remaining shell scripts: `rm -f ~/.local/bin/cocopack*`

## Shell Utilities

When installed with shell support, the following commands are available:

```bash
# Show available commands
cocopack --help

# Use shell utilities
cocopack ezshell    # Shell utility functions
cocopack prompt     # Custom prompt utilities
cocopack colorcode  # Color code utilities
cocopack jekyll     # Jekyll helper functions

# Python-wrapped commands
clear-git-history   # Clear git history
jekyll-restart      # Restart Jekyll server
jekyll-reload       # Reload Jekyll server
```

## Development

To contribute to this package:

1. Install Hatch if you haven't already:
```bash
pip install hatch
```

2. Clone the repository and enter the directory:
```bash
git clone https://github.com/ColinConwell/Coco-Pack.git
cd Coco-Pack
```

3. Create and activate a development environment:
```bash
hatch shell
```

4. Run tests:
```bash
hatch run test:test
```

5. Run style checks and type checking:
```bash
hatch run lint:check
```

6. Build documentation:
```bash
hatch run docs:build
```

## Sub-packages

### `notebook`

Contains utilities for working with Jupyter notebooks:

- `stylizer`: Automatic IDE-specific styling for Jupyter outputs
- `magics`: IPython magic commands and utilities

#### Examples

```python
# Apply IDE-specific styling
from cocopack.notebook import stylizer
stylizer.auto_style()

# Enable auto-reload for development
from cocopack.notebook import magics
magics.set_autoreload('complete')
```
