"""
Shell script installation and uninstallation utilities.
"""
import os, sys
import site
import atexit
from pathlib import Path

def get_shell_scripts_dir():
    """Get the directory where shell scripts are stored"""
    # First check if we're in development mode
    package_dir = Path(__file__).parent.parent
    shell_dir = package_dir / 'shell'
    
    if not shell_dir.exists():
        # Try repository root (for development installs)
        repo_root = Path(__file__).parent.parent.parent.parent
        shell_dir = repo_root / 'shell'
    
    if not shell_dir.exists():
        # Try installed shared-data location (for PyPI installs)
        import sys
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a virtual environment
            shared_data_dir = Path(sys.prefix) / 'share' / 'cocopack' / 'shell'
        else:
            # We're in a regular Python installation
            shared_data_dir = Path(sys.prefix) / 'share' / 'cocopack' / 'shell'
            
            # For user installs, also try user directory
            if not shared_data_dir.exists():
                try:
                    import site
                    user_base = Path(site.getuserbase()) if hasattr(site, 'getuserbase') else Path.home() / '.local'
                    shared_data_dir = user_base / 'share' / 'cocopack' / 'shell'
                except ImportError:
                    pass
        
        if shared_data_dir.exists():
            shell_dir = shared_data_dir
    
    return shell_dir if shell_dir.exists() else None

def get_bin_dir():
    """Get the directory where scripts should be installed"""
    # Use the same bin directory where pip installs scripts
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        bin_dir = Path(sys.prefix) / 'bin'
    else:
        # We're in a regular Python installation, use user directory
        bin_dir = Path(sys.prefix) / 'bin'
        
        # For user installs, use user bin directory
        if not os.access(bin_dir, os.W_OK):
            user_base = Path(site.getuserbase()) if hasattr(site, 'getuserbase') else Path.home() / '.local'
            bin_dir = user_base / 'bin'
            bin_dir.mkdir(parents=True, exist_ok=True)
    
    return bin_dir

def create_script_symlink(src_path, bin_dir, script_name, namespaced=True):
    """Create a wrapper script for a shell script
    
    Args:
        src_path: Path to the source script
        bin_dir: Directory to install wrapper to
        script_name: Name of the script
        namespaced: If True, prefix with 'cocopack-', otherwise use direct name
    """
    # Determine the destination path
    if namespaced:
        dest_path = bin_dir / f"cocopack-{script_name.replace('.sh', '')}"
    else:
        # For direct commands, use the simplified name
        script_base = script_name.replace('.sh', '')
        # Convert to kebab-case
        dest_path = bin_dir / f"{script_base.replace('_', '-')}"
    
    # Check if script exists
    if dest_path.exists():
        dest_path.unlink()  # Remove existing file or link
    
    # Always create a wrapper script instead of symlink for better compatibility
    with open(dest_path, 'w') as f:
        f.write(f"""#!/bin/bash
# This is an auto-generated wrapper for CocoPack
# Original script: {src_path}

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "CocoPack Shell Script: {script_name}"
    echo "Usage: $(basename $0) [arguments]"
    echo ""
    echo "This is a wrapper around {src_path}"
    exit 0
fi

# Source the script for functions
source "{src_path}"

# If the script contains a function with the same name as the file (without .sh)
# execute that function, otherwise just source the script
func_name="{script_name.replace('.sh', '')}"
if declare -f "$func_name" > /dev/null; then
    "$func_name" "$@"
elif declare -f "color_wrap" > /dev/null && [ "{script_name}" = "colorcode.sh" ]; then
    # Special case for colorcode.sh
    if [ $# -lt 2 ]; then
        echo "Usage: $(basename $0) COLOR TEXT"
        echo "  COLOR: color name (e.g., RED, BOLD_BLUE)"
        echo "  TEXT: the text to colorize"
        exit 1
    fi
    color_wrap "$1" "$2"
fi
""")
        os.chmod(dest_path, 0o755)  # Make executable

def create_python_command_wrapper(bin_dir, command_name, module_path, function_name, namespaced=True):
    """Create a wrapper script for a Python function
    
    Args:
        bin_dir: Directory to install wrapper to
        command_name: Name of the command (will be converted to kebab-case)
        module_path: Python module path
        function_name: Function name in the module
        namespaced: If True, prefix with 'cocopack-', otherwise use direct name
    """
    # Convert command_name to kebab-case if needed
    kebab_command = command_name.replace('_', '-')
    
    # Determine destination path
    if namespaced:
        dest_path = bin_dir / f"cocopack-{kebab_command}"
    else:
        dest_path = bin_dir / kebab_command
    
    # Check if script exists
    if dest_path.exists():
        dest_path.unlink()  # Remove existing file or link
    
    # Create wrapper script
    with open(dest_path, 'w') as f:
        f.write(f"""#!/usr/bin/env python
# This is an auto-generated wrapper for CocoPack
# Module: {module_path}
# Function: {function_name}

import sys
from {module_path} import {function_name}

if __name__ == "__main__":
    sys.exit({function_name}())
""")
        os.chmod(dest_path, 0o755)  # Make executable

def install_shell_scripts():
    """Install shell scripts to the bin directory (with namespace prefix)"""
    shell_dir = get_shell_scripts_dir()
    if not shell_dir:
        return  # No shell scripts directory found
    
    bin_dir = get_bin_dir()
    if not bin_dir:
        return  # No bin directory found
    
    # Install main shell scripts
    for script_file in shell_dir.glob('*.sh'):
        create_script_symlink(script_file, bin_dir, script_file.name, namespaced=True)
    
    # Install helper scripts
    helpers_dir = shell_dir / 'helpers'
    if helpers_dir.exists():
        for script_file in helpers_dir.glob('*.sh'):
            create_script_symlink(script_file, bin_dir, f"helpers-{script_file.name}", namespaced=True)
    
    # Install utility scripts
    scripts_dir = shell_dir / 'scripts'
    if scripts_dir.exists():
        for script_file in scripts_dir.glob('*.sh'):
            create_script_symlink(script_file, bin_dir, f"scripts-{script_file.name}", namespaced=True)
    
    print("Shell scripts installed with namespace prefix (cocopack-*).")
    print("To install direct commands, run: cocopack install")

def install_direct_scripts():
    """Install direct command scripts (without namespace prefix)"""
    from .cli import DIRECT_COMMANDS
    
    bin_dir = get_bin_dir()
    if not bin_dir:
        print("Error: Could not determine bin directory for script installation")
        return 1
    
    print("Installing direct command scripts...")
    count = 0
    
    # Install Python command wrappers
    for cmd_name, cmd_info in DIRECT_COMMANDS.items():
        if cmd_name in ['install', 'uninstall']:
            # Skip the meta-commands
            continue
            
        module_path = f"cocopack.shellpack.{cmd_info['module']}"
        function_name = cmd_info['function']
        
        try:
            create_python_command_wrapper(bin_dir, cmd_name, module_path, function_name, namespaced=False)
            print(f"Installed: {cmd_name}")
            count += 1
        except Exception as e:
            print(f"Error installing {cmd_name}: {e}")
    
    print(f"Successfully installed {count} direct command scripts.")
    print("These commands can now be used directly without the 'cocopack' prefix.")
    return 0

def uninstall_shell_scripts():
    """Uninstall shell scripts from the bin directory"""
    shell_dir = get_shell_scripts_dir()
    if not shell_dir:
        return  # No shell scripts directory found
    
    bin_dir = get_bin_dir()
    if not bin_dir:
        return  # No bin directory found
    
    # Remove main shell scripts (namespaced)
    for script_file in shell_dir.glob('*.sh'):
        script_name = script_file.name.replace('.sh', '')
        wrapper_path = bin_dir / f"cocopack-{script_name}"
        if wrapper_path.exists():
            try:
                wrapper_path.unlink()
                print(f"Removed wrapper: {wrapper_path}")
            except Exception as e:
                print(f"Failed to remove {wrapper_path}: {e}")
    
    # Remove helper scripts (namespaced)
    helpers_dir = shell_dir / 'helpers'
    if helpers_dir.exists():
        for script_file in helpers_dir.glob('*.sh'):
            wrapper_path = bin_dir / f"cocopack-helpers-{script_file.name.replace('.sh', '')}"
            if wrapper_path.exists():
                try:
                    wrapper_path.unlink()
                    print(f"Removed wrapper: {wrapper_path}")
                except Exception as e:
                    print(f"Failed to remove {wrapper_path}: {e}")
    
    # Remove utility scripts (namespaced)
    scripts_dir = shell_dir / 'scripts'
    if scripts_dir.exists():
        for script_file in scripts_dir.glob('*.sh'):
            wrapper_path = bin_dir / f"cocopack-scripts-{script_file.name.replace('.sh', '')}"
            if wrapper_path.exists():
                try:
                    wrapper_path.unlink()
                    print(f"Removed wrapper: {wrapper_path}")
                except Exception as e:
                    print(f"Failed to remove {wrapper_path}: {e}")
    
    # Also uninstall direct command scripts
    from .cli import DIRECT_COMMANDS
    
    # Remove Python command wrappers (direct)
    for cmd_name in DIRECT_COMMANDS:
        if cmd_name in ['install', 'uninstall']:
            # Skip the meta-commands
            continue
            
        kebab_cmd = cmd_name.replace('_', '-')
        wrapper_path = bin_dir / kebab_cmd
        if wrapper_path.exists():
            try:
                wrapper_path.unlink()
                print(f"Removed direct command: {wrapper_path}")
            except Exception as e:
                print(f"Failed to remove {wrapper_path}: {e}")

# Register the uninstall function to be called on package uninstall
# This will be triggered when pip runs the uninstall command
def register_uninstall():
    """Register the uninstallation function with atexit"""
    atexit.register(uninstall_shell_scripts)

# Try to register the uninstall hook when this module is imported
try:
    register_uninstall()
except Exception:
    # If registration fails, it's not critical
    pass

if __name__ == "__main__":
    install_shell_scripts()