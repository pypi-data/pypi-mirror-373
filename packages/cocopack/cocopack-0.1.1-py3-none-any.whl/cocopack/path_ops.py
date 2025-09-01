import os, sys

def diffpath(path, root):
    """Get the relative path between two paths.
    
    Args:
        path (str): The target path.
        root (str): The root path to compute the relative path from.
    
    Returns:
        str: The relative path from root to path.
    """
    # Convert both paths to absolute paths
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(root)
    return os.path.relpath(abs_path, abs_root)

def print_path_structure(root_dir, max_depth=2, include=None, exclude=None, **kwargs):
    """Print a hierarchical representation of a directory structure.
    
    Args:
        root_dir (str): Path to the root directory to display.
        max_depth (int, optional): Maximum depth of directories to display. Defaults to 2.
        include (Union[str, list], optional): Pattern(s) to include in the output.
            Only entries containing these patterns will be shown. Defaults to None.
        exclude (Union[str, list], optional): Pattern(s) to exclude from the output.
            Entries containing these patterns will be excluded. Defaults to None.
        **kwargs: Additional keyword arguments.
            whitespace (int): Number of spaces to add before each line. Defaults to 0.
    """
    root_dir_depth = root_dir.rstrip(os.sep).count(os.sep)  # Base depth of root directory

    def check_pattern(entry, patterns, exclude=False):
        if not isinstance(patterns, list):
            patterns = [patterns]
        match = any(pattern in entry for pattern in patterns)
        return match if not exclude else not match
    
    whitespace = ' ' * kwargs.pop('whitespace', 0)

    for root, dirs, files in os.walk(root_dir):
        current_depth = root.count(os.sep)
        if current_depth - root_dir_depth >= max_depth:
            dirs[:] = []  # Stop traversing further
            continue

        # Skip directories without files and beyond max_depth
        if not files and not dirs and current_depth - root_dir_depth >= max_depth - 1:
            continue

        # Determine the indentation level
        level = current_depth - root_dir_depth
        indent = '—' * (level + 1)

        entries = [] # add dirs + files

        # Aggregate entries
        subdir = os.path.basename(root)
        if subdir is not None:
            entries += [f"{whitespace} {indent} {subdir}/"]

        # Print files
        subindent = '—' * (level + 2)
        for file in files:
            entries += [f"{whitespace} {subindent} {file}"]

        # filter entries
        if include is not None:
            entries = [entry for entry in entries if check_pattern(entry, include, False)]

        if exclude is not None:
            entries = [entry for entry in entries if check_pattern(entry, exclude, True)]

        if len(entries) >= 1:
            print('\n'.join(entries))

def list_packages(pkg_names=[], dir_paths=None, pkg_types=['site-packages'], 
                  file_types=['.py'], other_filters=[], **kwargs):
    """List and display package structures from Python's import paths.
    
    Args:
        pkg_names (Union[str, list], optional): Name(s) of packages to list.
            If empty, all packages in found directories will be listed. Defaults to [].
        dir_paths (Union[str, list], optional): Directory paths to search for packages.
            If None, uses sys.path. Defaults to None.
        pkg_types (Union[str, list], optional): Types of package directories to look for.
            Defaults to ['site-packages'].
        file_types (Union[str, list], optional): File extensions to include in the output.
            Defaults to ['.py'].
        other_filters (Union[str, list], optional): Additional patterns to filter by.
            Defaults to [].
        **kwargs: Additional keyword arguments.
            global_root (str): Common root path for relative path display.
            max_depth (int): Maximum depth for print_path_structure. Defaults to 2.
    """
    if dir_paths is None or len(dir_paths) == 0: 
        dir_paths = sys.path # default to sys.path
        
    dir_paths = [path for path in dir_paths if len(path) >= 1]
        
    global_root = kwargs.pop('global_root', os.path.commonpath(dir_paths))
        
    if not isinstance(pkg_names, list):
        pkg_names = [pkg_names]
        
    if not isinstance(pkg_types, list):
        pkg_types = [pkg_types]
    
    if not isinstance(file_types, list):
        file_types = [file_types]
        
    if not isinstance(other_filters, list):
        other_filters = [other_filters]
        
    all_filters = file_types + other_filters
        
    def _pkg_type_check(path):
        return any(pkg_type in path for pkg_type in pkg_types)
    
    def _pkg_name_check(path):
        if not pkg_names:
            return True
        return any(pkg_name in path for pkg_name in pkg_names)
    
    def _pkg_check_combo(path):
        if not _pkg_type_check(path):
            return False
        
        for subpath in os.listdir(path):
            if _pkg_name_check(subpath):
                return True
        
    pkg_dirs = [path for path in dir_paths if _pkg_check_combo(path)]
    
    pkg_sets = set(pkg_dir for pkg_dir in pkg_dirs)
    
    for pkg_set in pkg_sets:
        pkg_set_name = diffpath(pkg_set, global_root)
        print(f"Packages from: {pkg_set_name}")
        if not pkg_names:
            pkg_names = os.listdir(pkg_set)
        
        for pkg_name in pkg_names:
            if pkg_name in os.listdir(pkg_set):
                print(f'  Package: {pkg_name}')
                package = os.path.join(pkg_set, pkg_name)
                print_path_structure(package, include=all_filters, whitespace=4, **kwargs)