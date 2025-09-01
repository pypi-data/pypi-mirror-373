# CocoPack <img src="logo.png" align="right" width="224px" height="224px" />

Programmatic toolkits for Python, R, and shell scripting. *CocoPack* (inspired by R's [`Hmisc` package](https://cran.r-project.org/web/packages/Hmisc/index.html)) provides a somewhat random collection of utilities to streamline development workflows that I (a *co*mputational *co*gnitive scientist) tend to use in many of my projects.

*Caveat Emptor*: The core functionality of this codebase is (largely) human-built and (entirely) human-tested. However, much of the documentation and supporting infrastructure (e.g. installation instructions) has been generated with ample help from [Claude AI](https://www.anthropic.com/). Please use with caution.

Functionality Status:
- [x] Python
- [x] Shell
- [x] R Pack

Documentation and source code for the [R](https://www.r-project.org/) package may be found at [colinconwell.github.io/Coco-Pack-R](https://colinconwell.github.io/CocoPack-R)

## Quick-Start

### Python Package

```bash
pip install cocopack
```

### R Package

```R
if (!require(pacman)) {install.packages("pacman")}
pacman::p_load_gh("colinconwell/Coco-Pack-R")
```

### Shell Commands

```bash
pip install "cocopack[shell]"
```

Shell scripts are installed automatically, but if needed, you can reinstall the shell script wrappers with:

```bash
cocopack-install
```

### Python + Shell

Install everything:

```bash
pip install "cocopack[shell]"
```

After installation, shell commands are available in two formats:

```bash
# Use shell commands directly
path-cleanup --remove-duplicates --apply
color-wrap RED "This text will be red!"

# Or use through the cocopack namespace
cocopack ezshell path_cleanup --remove-duplicates --apply
cocopack colorcode
```


### Python Package Only

Install just the Python utilities:
```bash
pip install cocopack
```

This also installs both direct and namespaced shell commands, but doesn't emphasize the shell functionality.

### Uninstallation

Remove everything:
```bash
# First, clean up shell script wrappers
cocopack uninstall-scripts

# Then uninstall the Python package
pip uninstall cocopack
```

This will remove both Python and shell components. You should also remove any references to cocopack commands from your .bashrc or .zshrc.

**Note**: When you run `pip uninstall cocopack`, the package will attempt to automatically clean up shell script wrappers, but it's recommended to run the explicit uninstall command first to ensure all wrappers are properly removed.

### R Package (CocoPack-R)

**Standalone Package**:

The `cocopack` R package is available at [CocoPack-R](https://colinconwell.github.io/CocoPack-R/).

You can install this package by running the following command:

```R
if (!require(pacman)) {install.packages("pacman")}
pacman::p_load_gh("colinconwell/CocoPack-R")
```

## Common Workflows

### Dev Environment Setup

1. Set up your shell environment:
```bash
# Add to .bashrc or .zshrc
eval "$(cocopack prompt)"  # Load prompt utilities
eval "$(cocopack ezshell)"  # Load shell utilities

# Configure custom prompt
PS1='$(conda_prompt green) %F{cyan}%n@%m%f $(custom_path) %# '
```

2. Configure Jupyter environment:
```python
from cocopack.notebook import stylizer, magics

# Apply IDE-specific styling
stylizer.auto_style()

# Enable auto-reload for development
magics.set_autoreload('complete')
```

### Path Management

```bash
# Clean up PATH environment variable
path_cleanup --remove-duplicates --remove-empties --apply
```

## Other Notes & Details

<details>
<summary><strong>Installation Options Explained</strong></summary>

1. **Standard Installation** (`pip install cocopack`):
   - Installs the Python package with all commands available
   - Both namespaced commands (e.g., `cocopack colorcode RED "text"`) and direct commands (e.g., `color-wrap RED "text"`) are available

2. **Shell Installation** (`pip install "cocopack[shell]"`):
   - Same as standard installation but emphasizes shell functionality
   - All commands are available in both namespaced and direct forms
</details>

### Presentation & Figure Support

The Python package includes presentation to image/PDF conversion functionality via the `figure_ops` module:

- Unified interface for both PowerPoint and Keynote presentations:
  - Automatically detects file type (.key, .ppt, .pptx)
  - Platform-specific implementations for optimal results

- Platform-specific exports:
  - macOS: Uses AppleScript for both Keynote and PowerPoint
  - Windows: Uses COM interface (via pywin32) for PowerPoint
  - Linux/Other: Uses LibreOffice CLI with python-pptx as fallback

- Image processing tools:
  - Cropping whitespace around images
  - Adding customizable margins
  - Converting to high-quality PDFs

Example usage:
```python
from cocopack.figure_ops import slides_to_images, convert_images_to_pdf

# Convert any presentation to PNGs and crop whitespace
slides_to_images('presentation.pptx', 'output_folder', crop_images=True)

# Convert to PDFs
convert_images_to_pdf('output_folder')
```

Note: Keynote is available exclusively on macOS. Windows users will need to install pywin32 separately if they want to use the Windows-specific COM automation:
```bash
pip install pywin32
```
