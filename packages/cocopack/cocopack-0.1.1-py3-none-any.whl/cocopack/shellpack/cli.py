import os, sys, subprocess, importlib
from pathlib import Path
from warnings import warn

from .install import uninstall_shell_scripts

# Core shell scripts
SHELL_COMMANDS = {
    'ezshell': 'ezshell.sh',
    'colorcode': 'colorcode.sh',
    'prompt': 'prompt.sh',
}

# Direct commands that can be run via the cocopack CLI
DIRECT_COMMANDS = {
    'color-wrap': {'module': 'commands', 'function': 'color_wrap'},
    'symlinks': {'module': 'commands', 'function': 'show_symlinks'},
    'storage': {'module': 'commands', 'function': 'show_storage'},
    'safe-remove': {'module': 'commands', 'function': 'safe_remove'},
    'rcd': {'module': 'commands', 'function': 'rcd'},
    'move-with-symlink': {'module': 'commands', 'function': 'move_with_symlink'},
    'split-path': {'module': 'commands', 'function': 'split_path'},
    'path-cleanup': {'module': 'commands', 'function': 'path_cleanup'},
    'install': {'module': 'install', 'function': 'install_direct_scripts'},
    'uninstall': {'module': 'install', 'function': 'uninstall_shell_scripts'},
}

def get_script_path(script_name):
    """Get the full path to a shell script"""
    # Use the same logic as install.py to find shell scripts
    from .install import get_shell_scripts_dir
    shell_dir = get_shell_scripts_dir()
    
    if shell_dir:
        script_path = shell_dir / script_name
        if script_path.exists():
            return script_path
    
    # If still not found, look in the installed scripts
    import shutil
    cmd_path = shutil.which(f"cocopack-{script_name.replace('.sh', '')}")
    if cmd_path:
        return Path(cmd_path)
    
    # Return a default path (though it won't exist)
    package_dir = Path(__file__).parent.parent
    return package_dir / 'shell' / script_name

def run_script(script_path, *args):
    """Run a shell script with arguments"""
    cmd = ['/bin/bash', str(script_path)] + list(args)
    subprocess.run(cmd, check=True)

def print_usage():
    """Print usage information"""
    print("Usage: cocopack <command> [args...]")
    
    print("\nShell script commands:")
    for cmd in sorted(SHELL_COMMANDS.keys()):
        print(f"  {cmd}")
    
    print("\nDirect commands:")
    for cmd in sorted(DIRECT_COMMANDS.keys()):
        print(f"  {cmd}")
    
    print("\nFor command-specific help:")
    print("  cocopack <command> --help")
    
    print("\nTo install direct commands (for use without 'cocopack' prefix):")
    print("  cocopack install")

def source_shell_script(script_path, *args):
    """Source a shell script and run a command"""
    script_name = Path(script_path).stem  # Get the name without extension
    
    # Handle help flag
    if args and (args[0] == '--help' or args[0] == '-h'):
        print(f"Help for {script_name}:")
        # For colorcode, display specific help
        if script_name == 'colorcode':
            print("Usage: cocopack colorcode COLOR TEXT")
            print("  COLOR: color name from the colorcode.sh script (e.g., RED, BOLD_BLUE)")
            print("  TEXT: the text to colorize")
            return 0
        # For other scripts, just source them and extract help
        cmd = f"source {script_path} && if [ \"$(type -t {script_name}_help)\" = function ]; then {script_name}_help; else echo 'No help available for {script_name}'; fi"
        return os.system(cmd)
    
    # For colorcode, handle the color_wrap function
    if script_name == 'colorcode':
        if len(args) < 2:
            print("Error: colorcode requires COLOR and TEXT arguments")
            print("Use 'cocopack colorcode --help' for more information")
            return 1
        text = ' '.join(args[1:])
        cmd = f"bash -c 'source {script_path} && color_wrap {args[0]} \"{text}\"'"
    else:
        # For other scripts, just source and run any commands
        cmd = f"source {script_path}"
        if args:
            cmd += f" && {' '.join(args)}"
    
    return os.system(cmd)

def run_direct_command(command, args):
    """Run a direct command from the commands module"""
    try:
        cmd_info = DIRECT_COMMANDS[command]
        module_name = f"cocopack.shellpack.{cmd_info['module']}"
        function_name = cmd_info['function']
        
        # Import the module dynamically
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        
        # Set sys.argv for the function (which might access it)
        old_argv = sys.argv
        sys.argv = [command] + args
        
        try:
            # Call the function
            result = function()
            if isinstance(result, int):
                return result
            return 0
        finally:
            # Restore sys.argv
            sys.argv = old_argv
    except (ImportError, AttributeError) as e:
        print(f"Error executing command '{command}': {e}")
        return 1

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]
    
    # Check if it's a direct command
    if command in DIRECT_COMMANDS:
        exit_code = run_direct_command(command, args)
        sys.exit(exit_code)
    
    # Check if it's a shell script command
    if command in SHELL_COMMANDS:
        script_path = get_script_path(SHELL_COMMANDS[command])
        if not script_path.exists():
            print(f"Script not found: {script_path}")
            sys.exit(1)
        
        # Pass remaining arguments to the script
        exit_code = source_shell_script(script_path, *args)
        sys.exit(exit_code >> 8)  # Convert shell exit code to Python exit code
    
    # Unknown command
    print(f"Unknown command: {command}")
    print_usage()
    sys.exit(1)

if __name__ == '__main__':
    main() 