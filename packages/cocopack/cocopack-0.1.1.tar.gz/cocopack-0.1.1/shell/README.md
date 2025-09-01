# Coco-Pack Shell (Coco-ShPack)

Shell utilities for Coco-Pack, available through the `cocopack` command when installed.

## Installation

Shell utilities are installed as part of the full Coco-Pack installation:
```bash
pip install "coco-pack[shell]"
```

## Usage

### Direct Commands (Default)

Use the shell commands directly:

```bash
# Use shell commands directly
path-cleanup --remove-duplicates --apply
color-wrap CYAN "This text will be cyan!"
```

### Namespaced Commands

Prepend `cocopack` `{subcommand}` to access the shell commands:

```bash
cocopack ezshell path_cleanup --remove-duplicates --apply
```

## Uninstallation

```bash
pip uninstall cocopack
```

After uninstallation:
1. Remove cocopack-related lines from your .bashrc or .zshrc
2. Clean up any remaining shell scripts (e.g.): `rm -f ~/.local/bin/cocopack*`
