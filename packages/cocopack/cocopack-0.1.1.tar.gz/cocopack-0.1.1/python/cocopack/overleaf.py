import os, io, re, shutil
import bibtexparser # 1.x

from copy import copy
from glob import glob
from pathlib import Path
from PIL import Image
from tqdm.auto import tqdm
from datetime import datetime

__all__ = [
    'set_overleaf_root',
    'get_overleaf_root', 
    'get_overleaf_path', 
    'list_overleaf_projects',
    'gather_submission', 
    'find_tex_inputs', 
    'find_all_inputs', 
    'stitch_tex_files', 
    'get_bibtex_dir', 
    'get_bibtex_files', 
    'clean_bibtex_file', 
    'stitch_bibtex_files']

from .convert import convert_image

# Initial Setup -----------------------------------------------------------

def set_overleaf_root(overleaf_root=None):
    """Set the root directory for Overleaf projects.
    
    Args:
        overleaf_root (str, optional): Path to the Overleaf root directory.
            If None, prompts the user to enter the directory. Defaults to None.
    """
    global OVERLEAF_ROOT
    if overleaf_root is not None:
        OVERLEAF_ROOT = overleaf_root
        
    else: # prompt user for root
        OVERLEAF_ROOT = input('Enter the Overleaf root directory: ')
    
def _check_overleaf_root():
    overleaf_root_found = False
    overleaf_root_valid = False

    if 'OVERLEAF_ROOT' in globals():
        overleaf_root_found = True

    if 'OVERLEAF_ROOT' in os.environ:
        overleaf_root_found = True

    overleaf_root_abspath = os.path.abspath(OVERLEAF_ROOT)

    if os.path.exists(overleaf_root_abspath):
        overleaf_root_valid = True

    return overleaf_root_found and overleaf_root_valid

def _check_bibtexparser_version():
    return bibtexparser.__version__.startswith('1')

if not _check_bibtexparser_version():
    raise ImportError("bibtexparser1.x, To fix, try:",
                      "\npip install bibtexparser~=1.0")

# Core Functions ----------------------------------------------------------

def get_overleaf_root(overleaf_root=None):
    """Get the root directory for Overleaf projects.
    
    Args:
        overleaf_root (str, optional): Path to the Overleaf root directory.
            If provided, returns this value. Defaults to None.
    
    Returns:
        str: Path to the Overleaf root directory. If not provided, tries to get it from
            globals, environment variables, or prompts the user.
    """
    if overleaf_root is None: # fetch from globals
        if 'OVERLEAF_ROOT' in globals():
            return globals().get('OVERLEAF_ROOT')

        if 'OVERLEAF_ROOT' in os.environ:
            return os.environ.get('OVERLEAF_ROOT')
            
        else: # prompt user for root
            set_overleaf_root()
            _check_overleaf_root()
    
    return overleaf_root

def get_overleaf_path(project_name, overleaf_root=None):
    """Get the full path to an Overleaf project.
    
    Args:
        project_name (str): Name of the Overleaf project.
        overleaf_root (str, optional): Path to the Overleaf root directory.
            If None, gets it from get_overleaf_root(). Defaults to None.
    
    Returns:
        str: Full path to the Overleaf project.
    """
    overleaf_root = get_overleaf_root(overleaf_root)
    return os.path.join(overleaf_root, project_name)

def list_overleaf_projects(overleaf_root=None, exclusions=[], sort_by_date=True, **kwargs):
    """List all Overleaf projects in the root directory.
    
    Args:
        overleaf_root (str, optional): Path to the Overleaf root directory.
            If None, gets it from get_overleaf_root(). Defaults to None.
        exclusions (list, optional): List of strings to filter out projects containing these substrings.
            Defaults to an empty list.
        sort_by_date (bool, optional): Whether to sort projects by modification date. Defaults to True.
        **kwargs: Additional keyword arguments.
            verbose (bool): If True, prints projects with their last modified dates. Defaults to False.
    
    Returns:
        list: List of Overleaf project names.
    """
    overleaf_root = get_overleaf_root(overleaf_root) # fetch root
    
    overleaf_paths = [(os.path.getmtime(path), path) for path
                      in glob(os.path.join(overleaf_root, '*'))]
    
    project_list = [(date, os.path.basename(path)) for date, path 
                    in overleaf_paths if os.path.isdir(path)]
    
    if exclusions is not None and len(exclusions) > 0:
        project_list = [(date, project) for date, project in project_list 
                        if not any([ex in project for ex in exclusions])]
            
    if sort_by_date: # return projects in order of modification:
        project_list = sorted(project_list, reverse=True)
        
        if kwargs.pop('verbose', False):
            for date, project in project_list:
                date = (datetime.fromtimestamp(date)
                        .strftime('%Y-%m-%d'))
                print(f'{project}: Last Modified {date}')
    
    return [project for date, project in project_list]

def get_overleaf_projects(overleaf_root=None, exclusions=[], sort_by_date=True, **kwargs):
    """Alias for list_overleaf_projects. Lists all Overleaf projects in the root directory.
    
    Args:
        overleaf_root (str, optional): Path to the Overleaf root directory.
            If None, gets it from get_overleaf_root(). Defaults to None.
        exclusions (list, optional): List of strings to filter out projects containing these substrings.
            Defaults to an empty list.
        sort_by_date (bool, optional): Whether to sort projects by modification date. Defaults to True.
        **kwargs: Additional keyword arguments.
            verbose (bool): If True, prints projects with their last modified dates. Defaults to False.
    
    Returns:
        list: List of Overleaf project names.
    """
    return list_overleaf_projects(overleaf_root, exclusions, sort_by_date, **kwargs)

# Gather Submission Materials ---------------------------------------------

def gather_submission(project_path, main_file, support_files, output_dir, **kwargs):
    """Gather LaTeX project files for submission, stitching files together and organizing references.
    
    Args:
        project_path (str): Path to the project root directory.
        main_file (str): Name of the main LaTeX file.
        support_files (list): List of supporting files to include (images, bibtex, etc.).
        output_dir (str): Directory where gathered submission will be saved.
        **kwargs: Additional keyword arguments.
            prepend_project (bool): If True, prepend project_path to output_dir. Defaults to False.
            fresh_start (bool): If True, clear the output directory if it exists. Defaults to True.
            main_name (str): Name for the output main file. Defaults to 'manuscript.tex'.
            new_names (dict): Map of original filenames to new filenames. Defaults to {}.
            image_format (str): Convert images to this format if specified. Defaults to None.
            verbose (bool): If True, print detailed information. Defaults to False.
            stitch_bibtex (bool): If True, stitch bibtex files together. Defaults to True.
            exclude_comments (bool): If True, exclude commented lines when updating references. Defaults to True.
    """
    if kwargs.pop('prepend_project', False):
        output_dir = os.path.join(project_path, output_dir)
        
    output_root = Path(output_dir).parent
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    else: # clear the output directory
        if kwargs.get('fresh_start', True):
            if kwargs.get('verbose', True):
                print('Clearing the output directory:', output_dir)
            shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
    
    new_main = kwargs.pop('main_name', 'manuscript.tex')
    
    # Stitch (but don't yet write) main file .tex content
    content = stitch_tex_files(project_path, main_file, 
                                content_only=True, **kwargs)

    original_to_new = {} # file_path mappings
    
    #optional renaming schema for materials
    new_names = kwargs.pop('new_names', {})
    
    image_extensions = Image.registered_extensions()
    image_format = kwargs.pop('image_format', None)

    # Copy files to the output directory, flattening the structure
    for file_path in support_files:
        original_dir, filename = os.path.split(file_path)
        filename = new_names.get(filename, filename)
        new_path = os.path.join(output_dir, filename)

        # Check if there's a file name clash and handle it
        if not os.path.exists(new_path):
            base, ext = os.path.splitext(filename)
            count = 1 # add as suffix to new_path
            
            while os.path.exists(new_path):
                new_filename = f"{base}_{str(count).zfill(2)}{ext}"
                new_path = os.path.join(output_dir, new_filename)
                count += 1 # iter-update the file count

        # Copy the file
        src_path = os.path.join(project_path, file_path)
    
        shutil.copyfile(src_path, new_path)
        original_to_new[file_path] = new_path
        
    image_files = [file_path for file_path in original_to_new if 
                   os.path.splitext(file_path)[1] in image_extensions]
    
    if image_format is not None: # convert images to target format
        description = f'Converting Images to {image_format.upper()}'
        
        for file_path in tqdm(image_files, desc=description):
            if file_path.endswith(image_format): continue
            
            new_path = original_to_new[file_path]
            convert_image(new_path, image_format)
            
            _, src_ext = os.path.splitext(new_path)
            new_path = new_path.replace(src_ext, f'.{image_format}')
            
            original_to_new[file_path] = new_path # update the mapping
            
    last_bibliography = r'\\bibliography\{references\}'
                
    # Update references in the content
    for old_path, new_path in original_to_new.items():
        new_path = os.path.basename(new_path) # relative
        
        new_name, _ = os.path.splitext(new_path)
        old_name, _ = os.path.splitext(old_path)

        search_result = search_for_input(old_path, content, **kwargs)
        
        if search_result is not None:
            match_base = search_result['match_base']
            context = search_result['in_command']
            extension_included = '.' in match_base
            
            if extension_included: # update with path
                update = context.replace(old_path, new_path)
                
            else: # update with name only
                update = context.replace(old_name, new_name)
                
            if kwargs.get('exclude_comments', True):
                if context.startswith('%'):
                    continue # skip commented lines
                
            new_string = new_path if '.' in match_base else new_name
            
            if kwargs.get('verbose', False):
                print(f"Updating {match_base} to {new_string}"+
                      f" in {context}:\n  -> {update}")
            
            content = content.replace(context, update)
            
            if 'bibliography' in update:
                last_bibliography = copy(update)
            
    if kwargs.pop('stitch_bibtex', True):
        bibtex_files = get_bibtex_files(output_root, output_dir)
        output_file = os.path.join(output_dir, 'references.bib')
        
        if kwargs.get('verbose', False): 
            print(f'Stitching {len(bibtex_files)} to {output_file}...')
        
        stitch_bibtex_files(project_path, bibtex_files, output_file,
                            cleanup=True, dry_run=False)
        
        new_bibliography = "\\bibliography{references}"
        content = content.replace(last_bibliography, new_bibliography)
        
        if kwargs.get('verbose', True):
            print(f"Updating {last_bibliography} to {new_bibliography}")
                
    write_content(os.path.join(output_dir, new_main), content)

# Find Document Input -----------------------------------------------------

def get_command_regex(search, input_only=False):
    latex_commands = [r'\\input', r'\\usepackage', r'\\bibliography', r'\\includegraphics']
    if input_only: latex_commands = [r'\\input']
    command_pattern = f"({'|'.join(latex_commands)})"
    
    return (rf"(?:% *\s*)?{command_pattern}(?:\[[^\]]*\])?"+
            rf"\{{.*?\b{re.escape(search)}(\.\w+)?\b.*?\}}")

def search_for_input(file_path, content, **kwargs):
    base_name, extension = os.path.splitext(file_path)
    
    search_pattern = get_command_regex(base_name)
    matches = re.finditer(search_pattern, content)
        
    results = None # default to None
    all_results = [] # if multiple
    
    for match in matches:
        if kwargs.get('ignore_comments', True):
            if match.group(0).startswith('%'):
                continue # skip commented lines
            
        match_name = copy(base_name)
            
        if extension in match.group(0):
            match_name += extension
                
        results = {'match_base': match_name,
                   'in_command': match.group(0)}
        
        all_results += [results]
        
    if len(all_results) > 1:
        print('Warning: Multiple matches found for', file_path)

    return results # dictionary with match_context

def find_tex_inputs(project_dir, main_file='main.tex', depth=0, **kwargs):
    """Recursively find all LaTeX \input{} commands in a main file and its included files.
    
    Args:
        project_dir (str): Path to the project directory.
        main_file (str, optional): Name of the main LaTeX file. Defaults to 'main.tex'.
        depth (int, optional): Current recursion depth. Defaults to 0.
        **kwargs: Additional keyword arguments.
            max_depth (int): Maximum recursion depth. Defaults to 5.
            prepend_path (bool): If True, prepend the directory path to input files. Defaults to False.
    
    Returns:
        dict: Nested dictionary representing the structure of the LaTeX files and their inputs.
    """
    max_depth = kwargs.get('max_depth', 5)
    
    if depth > max_depth:
        print(f"Warning: Maximum recursion depth reached at {main_file}. Stopping.")
        return {}

    file_path = os.path.join(project_dir, main_file)
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}. Skipping...")
        return {}

    with open(file_path, 'r') as file:
        content = file.read()

    # initialize the structure at the main file
    structure = {main_file: {"path": file_path,
                             "inputs": {}}}

    # Find all \input{} commands
    inputs = re.findall(r'(?:%\s*)?\\input\{(.+?)\}', content)
    
    for input_file in inputs:
        search_result = search_for_input(input_file, content, **kwargs)
        
        if search_result is None:
            continue # skip this file
        
        if not input_file.endswith('.tex'):
            input_file += '.tex'
        input_path = copy(input_file)
        if kwargs.get('prepend_path', False):
            input_path = os.path.join(os.path.dirname(file_path), input_file)
        
        # Recursively process the input file
        sub_structure = find_tex_inputs(project_dir, input_path, 
                                        depth+1, **kwargs)
        
        structure[main_file]["inputs"].update(sub_structure)

    return structure

def find_all_inputs(project_path, main_file, stitch_first=False, **kwargs):
    """Find all files referenced in a LaTeX document through various commands.
    
    This function scans a LaTeX document for references to other files through commands like
    \input, \includegraphics, \bibliography, etc.
    
    Args:
        project_path (str): Path to the project directory.
        main_file (str): Name of the main LaTeX file.
        stitch_first (bool, optional): If True, stitch all input files before searching.
            Defaults to False.
        **kwargs: Additional keyword arguments.
            exclusions (list): List of strings to exclude files containing these substrings.
            files_only (bool): If True, return only file paths without match context. Defaults to False.
    
    Returns:
        Union[dict, list]: Either a dictionary mapping file paths to their match context,
            or a list of file paths if files_only=True.
    """
    # List all non-hidden files recursively in the project path
    all_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, project_path)
            if not relative_path.startswith('.'):
                if not file == main_file:
                    all_files.append(relative_path)
                    
    main_filepath = os.path.join(project_path, main_file)
        
    if not stitch_first: # Read the contents of the main file
        content = read_content(main_filepath)
        
    else: # Stitch together all \inputs to main file first
        content = stitch_tex_files(project_path, main_file, 
                                    content_only=True, **kwargs)
        
    results = {} # Dictionary to hold the results

    for relative_path in all_files:
        search_result = search_for_input(relative_path, content, **kwargs)
        
        if search_result is not None:
            results[relative_path] = search_result
            
    if kwargs.get('exclusions', None):
        def check_exclusion(entry):
            return any(exc in entry for exc in kwargs['exclusions'])
        
        results = {key: value for key, value in results.items()
                   if not check_exclusion(key)}
        
    if kwargs.get('files_only', False):
        return list(results.keys()) # file_paths
    
    return results # dictionary with file paths and match context

# Stitch Tex Documents ----------------------------------------------------

def write_content(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
        
def read_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content # from document

def update_paths(project_path, tex_file, updates, **kwargs):
    content = read_content(os.path.join(project_path, tex_file))
    
    for previous, update in updates.items():
        if kwargs.get('verbose', False):
            print(f"Updating {previous} to {update}")
        content = content.replace(previous, update)
        
    write_content(os.path.join(project_path, tex_file), content)

def stitch_tex_files(project_dir, main_file='main.tex', output_file=None, **kwargs):
    """Stitch together a LaTeX document by resolving all \input commands.
    
    Args:
        project_dir (str): Path to the project directory.
        main_file (str, optional): Name of the main LaTeX file. Defaults to 'main.tex'.
        output_file (str, optional): Path where the stitched file will be saved.
            If None, the function will only return the content. Defaults to None.
        **kwargs: Additional keyword arguments.
            exclude_with_comment (list): List of patterns to comment out instead of including.
            exclude (list): List of patterns to exclude from stitching.
            verbose (bool): If True, print detailed information. Defaults to False.
            content_only (bool): If True, only return the content without writing to a file. Defaults to True.
    
    Returns:
        str: The stitched LaTeX content.
    """
    comment_exclude = kwargs.pop('exclude_with_comment', [])
    exclusions = kwargs.get('exclude', [])
    
    verbose = kwargs.get('verbose', False)
    
    def process_file(file_info):
        file_path = file_info['path']
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace \input{} commands
        for input_file, input_info in file_info['inputs'].items():
            if verbose: print(f"Stitching \\input{{{input_file}}}")
            base_name, extension = os.path.splitext(input_file)
            
            if any([exc in input_file for exc in exclusions]):
                continue # skip rewriting of this file
            
            search_pattern = get_command_regex(base_name, True)
                
            if any([exc in search_pattern for exc in comment_exclude]):
                sub_args = (search_pattern, lambda x: f"%{x.group(0)}")
                content = re.sub(*sub_args, content); continue
                
            search_result = search_for_input(input_file, content, **kwargs)
            if search_result is None:
                continue # skip this file
            
            input_content = process_file(input_info)
            
            content = re.sub(search_pattern, lambda m: input_content, content)

        return content

    # Process the main file (first key in the structure)
    structure = find_tex_inputs(project_dir, main_file, **kwargs)
    main_file_info = structure[main_file]
    
    stitched_content = process_file(main_file_info)
    
    if kwargs.pop('content_only', True) or output_file is None:
        return stitched_content # return directly

    # Write the stitched content to the output file
    if '/' in output_file: # create new subdir
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
    output_file = os.path.join(project_dir, output_file)
    
    with open(output_file, 'w') as file:
        file.write(stitched_content)

    print(f"Stitched file created: {output_file}")

# Manage Bibtex Files -----------------------------------------------------

def get_bibtex_dir(project_name, bibtex_dir='citation', **kwargs):
    """Get the path to the directory containing BibTeX files for a project.
    
    Args:
        project_name (str): Name of the Overleaf project.
        bibtex_dir (str, optional): Name of the directory containing BibTeX files. 
            Defaults to 'citation'.
        **kwargs: Additional keyword arguments.
            overleaf_root (str): Path to the Overleaf root directory.
    
    Returns:
        str: Path to the BibTeX directory.
    """
    overleaf_root = kwargs.pop('overleaf_root', None)
    overleaf_root = get_overleaf_root(overleaf_root)
    
    return os.path.join(overleaf_root, project_name, bibtex_dir)

def get_bibtex_files(project_path, bibtex_dir, other_dirs=[]):
    """Get a list of BibTeX files in the specified directories.
    
    Args:
        project_path (str): Path to the project root directory.
        bibtex_dir (str): Name of the primary directory containing BibTeX files.
        other_dirs (list, optional): List of additional directories to search for BibTeX files.
            Defaults to an empty list.
    
    Returns:
        list: List of relative paths to BibTeX files.
    """
    # Process target bibtex directories + files:
    directories, bibtex_files = [bibtex_dir], []
    
    if (other_dirs is not None and len(other_dirs) > 0):
        directories += [directory for directory in other_dirs]
        
    for directory in directories:
        search_string = f'{project_path}/{directory}'
        if directory is None:
            search_string = f'{project_path}'
            
        bibtex_files += glob(f'{search_string}/*.bib')
        
    # make all paths relative to project path
    bibtex_files = [os.path.relpath(file_path, project_path) 
                    for file_path in bibtex_files]
        
    return bibtex_files # from primary + other directories

def clean_bibtex_file(input_file_path, output_file_path=None):
    """Remove commented lines from a BibTeX file.
    
    Args:
        input_file_path (str): Path to the input BibTeX file.
        output_file_path (str, optional): Path where the cleaned file will be saved.
            If None, returns the cleaned content as a StringIO object. Defaults to None.
    
    Returns:
        io.StringIO: StringIO object containing the cleaned content if output_file_path is None,
            otherwise None.
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cleaned_content = []
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line.startswith('%'):
            cleaned_content.append(line)

    if output_file_path:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(cleaned_content)
    else: # Return as StringIO if no output_file specified
        return io.StringIO(''.join(cleaned_content))
    
def parse_bibtex_file(bibtex_content, backend='bibtexparser'):
    """Parse BibTeX content using the specified backend.
    
    Args:
        bibtex_content (Union[str, io.StringIO]): BibTeX content as a string or StringIO object.
        backend (str, optional): Backend library to use for parsing.
            Options are 'bibtexparser' or 'pybtex'. Defaults to 'bibtexparser'.
    
    Returns:
        object: Parsed BibTeX database object (type depends on the backend used).
    
    Raises:
        ValueError: If the specified backend is not supported.
    """
    from pybtex.database import parse_string
    import bibtexparser # assumed version 1.X 
    
    if isinstance(bibtex_content, io.StringIO):
        bibtex_content.seek(0)  # Ensure buffer is ready to read from the beginning
        bibtex_content = bibtex_content.read()

    if backend == 'bibtexparser':
        with io.StringIO(bibtex_content) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        return bib_database
    elif backend == 'pybtex':
        bib_database = parse_string(bibtex_content, 'bibtex')
        return bib_database
    else: # raise error if backend not supported
        raise ValueError("Unsupported backend specified.")
    
# Stitch Bibtex Files -----------------------------------------------------

def stitch_bibtex_files(project_path, bibtex_files, output_file,
                        cleanup=False, dry_run=True, **kwargs):
    """Combine multiple BibTeX files into a single file, removing duplicates.
    
    Args:
        project_path (str): Path to the project root directory.
        bibtex_files (Union[str, list]): Either a directory containing BibTeX files
            or a list of BibTeX file paths.
        output_file (str): Path where the stitched file will be saved.
        cleanup (bool, optional): If True, delete or backup the original files. Defaults to False.
        dry_run (bool, optional): If True, don't write the stitched file or perform cleanup.
            Defaults to True.
        **kwargs: Additional keyword arguments.
            prepend_project (bool): If True, prepend project_path to output_file. Defaults to True.
            backup_dir (str): Directory where original files will be backed up, if cleanup is True.
            verbose (bool): If True, print detailed information. Defaults to False.
    
    Returns:
        None
    """
    if kwargs.get('prepend_project', True):
        output_file = os.path.join(project_path, output_file)

        if isinstance(bibtex_files, str):
            if os.path.isdir(bibtex_files):
                if project_path[:1] not in bibtex_files:
                    bibtex_files = os.path.join(project_path, bibtex_files)

        else: # assume list of files
            for index in range(len(bibtex_files)):
                bibtex_files[index] = os.path.join(project_path, bibtex_files[index])
            
    if not dry_run: # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
    stitched_entries = {}
    files_to_process = []

    if isinstance(bibtex_files, str):
        if os.path.isdir(bibtex_files):
            files_to_process = get_bibtex_files(project_path, bibtex_files)
    
    else: # assume list of files
        files_to_process = copy(bibtex_files)

    # Read all .bib files and accumulate unique entries
    for file_path in files_to_process:
        with open(file_path, 'r') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
            
            if kwargs.get('verbose', False): # of entries fetched
                print(f"{len(bib_database.entries)} entries fetched",
                      f"from {os.path.basename(file_path)}")

            for entry in bib_database.entries:
                entry_id = entry.get('ID', None)
                if entry_id and entry_id not in bibtex_files:
                    stitched_entries[entry_id] = entry
                    
    if kwargs.get('verbose', False) or dry_run: 
        # report number of unique entries
        print(f"{len(stitched_entries)} unique entries across",
              f"{len(files_to_process)} bibtex files")

    if not dry_run: # Write unique entries to output_file
        with open(output_file, 'w') as write_file:
            writer = bibtexparser.bwriter.BibTexWriter()
            db = bibtexparser.bibdatabase.BibDatabase()
            
            db.entries = list(stitched_entries.values())
            write_file.write(writer.write(db)) # stitch
            
            print(f"Bibtex entries stitched to: {output_file}")
            
    else: # Report the output file name without writing
        print(f"Dry-Run: Entries stitched to {output_file}")

    if cleanup: # delete or move stitched files to backup
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        if kwargs.get('backup_dir', None) is not None:
            backup_dir = kwargs.get('backup_dir')
            output_dir = f'{Path(output_file).parent.parent}/{backup_dir}'
        
            backup_dir = f"{output_dir}/backup/{timestamp}"
            
            if not dry_run: # build the backup directory
                os.makedirs(backup_dir, exist_ok=True)
                for file_path in files_to_process:
                    dst = os.path.join(backup_dir, os.path.basename(file_path))
                    shutil.move(file_path, dst)
            
                    if kwargs.get('verbose', False):
                        print(f"Moving {file_path} to {dst}")
                        
            else: # report the move without actually moving
                for file_path in files_to_process:
                    print(f"Would move {file_path} to {backup_dir}")
                    
        else: # delete the stitched files
            for file_path in files_to_process:
                action_report = 'Would delete'
                
                if not dry_run: # delete file
                    os.remove(file_path)
                    action_report = 'Deleting'
                    
                if kwargs.get('verbose', False):
                    print(f"{action_report} {file_path}")