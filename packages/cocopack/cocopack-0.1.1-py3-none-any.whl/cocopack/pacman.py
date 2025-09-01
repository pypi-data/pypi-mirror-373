import os, shutil
import json, tarfile
from glob import glob
from itertools import chain
from tqdm.auto import tqdm

def delete_git_files(folder_path, dry_run=True):
    """Delete all Git-related files and directories in a given folder.
    
    Args:
        folder_path (str): Path to the folder to clean.
        dry_run (bool, optional): If True, only print the files that would be deleted
            without actually deleting them. Defaults to True.
    """
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in dirs + files:
            if name.startswith('.git'):
                path_to_remove = os.path.join(root, name)
                
                if dry_run: # print the files to delete
                    print(f'Would remove: {path_to_remove}')
                    
                else: # actually delete the files
                    print(f'Removing  {path_to_remove}')
                    
                    if os.path.isdir(path_to_remove):
                        shutil.rmtree(path_to_remove)
                        
                    else: # the path is a file
                        os.remove(path_to_remove)

def delete_ipynb_checkpoints(target_dir, dry_run=True):
    """Delete all Jupyter Notebook checkpoint directories in a given folder.
    
    Args:
        target_dir (str): Path to the directory to clean.
        dry_run (bool, optional): If True, only print the directories that would be deleted
            without actually deleting them. Defaults to True.
    """
    for root, dirs, files in os.walk(target_dir):
        for dir in dirs:
            if dir == '.ipynb_checkpoints':
                checkpoint_folder = os.path.join(root, dir)
                
                if dry_run: # print the folders to be deleted
                    print(f"Would delete {checkpoint_folder}")
                    
                else: # actually delete the folders
                    shutil.rmtree(checkpoint_folder)
                    print(f"Deleted {checkpoint_folder}")

def remove_kernel_metadata(notebook_path):
    """Remove kernel specification metadata from a Jupyter notebook.
    
    Args:
        notebook_path (str): Path to the Jupyter notebook file.
    """
    # Load the notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    # Remove the kernelspec metadata
    if 'kernelspec' in notebook['metadata']:
        del notebook['metadata']['kernelspec']

    # Save the modified notebook
    with open(notebook_path, 'w') as f:
        json.dump(notebook, f, indent=4)
        
def insert_colab_metadata(notebook_path):
    """Insert Google Colab metadata into a Jupyter notebook.
    
    This function adds metadata that configures the notebook to use GPU acceleration
    with a T4 GPU type when opened in Google Colab.
    
    Args:
        notebook_path (str): Path to the Jupyter notebook file.
    """
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
        
    if 'kernelspec' in notebook['metadata']:
        del notebook['metadata']['kernelspec']
        
    kernelspec = {"name": "python3",
                  "display_name": "Python 3"}
    
    notebook['metadata']['kernelspec'] = kernelspec
    
    notebook['metadata']['accelerator'] = "GPU"
    
    notebook['metadata']['colab'] = {"provenance": [],
                                     "gpuType": "T4"}
    
    with open(notebook_path, 'w') as f:
        json.dump(notebook, f, indent=4)

def clear_ipynb_checkpoints(project_dir, dry_run=True):
    """Delete all Jupyter Notebook checkpoint directories in a project.
    
    Args:
        project_dir (str): Path to the project directory to clean.
        dry_run (bool, optional): If True, only print the directories that would be deleted
            without actually deleting them. Defaults to True.
    """
    delete_ipynb_checkpoints(project_dir, dry_run)

def clean_project_notebooks(project_dir, dry_run=True):
    """Clean Jupyter notebooks in a project by inserting Colab metadata.
    
    Args:
        project_dir (str): Path to the project directory containing notebooks.
        dry_run (bool, optional): If True, only print the notebooks that would be modified
            without actually modifying them. Defaults to True.
    """
    for notebook_path in glob(f'{project_dir}/**/*.ipynb', recursive=True):
        if dry_run: # names only
            print('Would clean:', notebook_path)
            
        else: # apply cleanup ops
            insert_colab_metadata(notebook_path)
            #remove_kernel_metadata(notebook_path)

def clear_git_files(project_dir, dry_run=True):
    """Delete all Git-related files and directories in a project.
    
    Args:
        project_dir (str): Path to the project directory to clean.
        dry_run (bool, optional): If True, only print the files that would be deleted
            without actually deleting them. Defaults to True.
    """
    delete_git_files(project_dir, dry_run)

def tar_files(source, filename, include=None, exclude=None, 
              hidden=False, fmt='bz2', dry_run=True):
    """Create a tar archive of files from a source directory or list of files.
    
    Args:
        source (Union[str, list]): Either a directory path or a list of file paths to include.
        filename (str): Base name for the output tar file (without extension).
        include (list, optional): List of patterns to include in the archive. 
            If provided, only files matching these patterns will be included. Defaults to None.
        exclude (list, optional): List of patterns to exclude from the archive.
            Files matching these patterns will be excluded. Defaults to None.
        hidden (bool, optional): If True, include hidden files (starting with '.'). 
            Defaults to False.
        fmt (str, optional): Compression format to use ('bz2' or 'gz'). Defaults to 'bz2'.
        dry_run (bool, optional): If True, only return the list of files that would be included
            without creating the archive. Defaults to True.
    
    Returns:
        list: If dry_run is True, returns the list of files that would be included.
        
    Raises:
        ValueError: If an unsupported format is specified or if source is invalid.
    """
    if include is None:
        include = []
    if exclude is None:
        exclude = []

    # Define tar file mode based on the format:
    mode = 'w' # write
    if fmt == 'bz2':
        mode += ':bz2'
    elif fmt == 'gz':
        mode += ':gz'
    else: # Invalid format
        raise ValueError("Unsupported format. Use 'bz2' or 'gz'.")

    # Prep file_list:
    files_to_tar = []
    if isinstance(source, str) and os.path.isdir(source):
        for root, dirs, files in os.walk(source):
            for name in files:
                if not hidden and name.startswith('.'):
                    continue # skip this file
                    
                file_path = os.path.join(root, name)
                
                if exclude and len(exclude) >= 1:
                    if any(pattern in file_path 
                           for pattern in exclude):
                        continue # skip this file
                    
                if include and len(include) >= 1:
                    if not any(pattern in file_path
                                for pattern in include):
                        continue # skip this file

                files_to_tar.append(file_path) # add to keep
                    
    elif isinstance(source, list):
        files_to_tar = source
        
    else: # Invalid argument
        raise ValueError("Source must be a directory path or a list of file paths.")

    output_file = f'{filename}.tar.' + fmt
    print(f'Tarring files to: {output_file}')
    output_dir = os.path.dirname(output_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if dry_run: # Return the specified file_list
        print('dry-run: these files specified:')
        return files_to_tar

    # Create the tar file
    with tarfile.open(output_file, mode) as tar:
        desc = 'Building Tar Archive (Files)'
        for file_path in tqdm(files_to_tar, desc):
            tar.add(file_path)

def get_file_size(file_path, unit_format='MB'):
    """Get the size of a file in the specified unit format.
    
    Args:
        file_path (str): Path to the file.
        unit_format (str, optional): Unit to return the size in.
            Options are 'B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'. 
            Defaults to 'MB'.
    
    Returns:
        float: Size of the file in the specified unit.
        
    Raises:
        ValueError: If an unsupported unit format is specified.
    """
    exponents = {'B': 0, 'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4, 
                 'PB': 5, 'EB': 6, 'ZB': 7, 'YB': 8}

    units = list(exponents.keys())

    if unit_format and unit_format not in units:
        raise ValueError(f'unit_format must be one of {units}')

    size_in_bytes = os.path.getsize(file_path)
    return size_in_bytes / (1024 ** exponents[unit_format])

def _get_extensions():
    extensions = {
        'image': ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp', '.gif', '.svg'],
        'video': ['.mp4', '.mov', '.mpg', '.mpeg', '.avi', '.wmv', '.webm', '.mkv', '.flv'],
        'audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
        'array': ['.npy', '.npz', '.pt', '.h5', '.mat'],
        'text': ['.txt', '.md', '.rtf', '.pdf', '.doc', '.docx'],
        'data': ['.csv', '.json', '.sql', '.pkl', '.hdf', '.hdf5', 
                 '.parquet', '.xls', '.xlsx', '.xlsm', '.xlsb', '.rdata'],
        'archive': ['.zip', '.tar', '.tar.gz', '.rar', '.7z', '.bz2', '.gz'],
        'checkpoint': ['.pyc', '.ckpt', '.ipynb_checkpoints', '__pycache__'],
        'executable': ['.exe', '.dll', '.so', '.bin'],
        'script': ['.py', '.js', '.html', '.css', '.sh', '.bat','.m'],
    }

    store_exts = [extensions[key] for key in
                  ['array', 'checkpoint', 'data', 'archive']]
    
    extensions['store'] = list(chain(*store_exts))

    media_exts = [extensions[key] for key in 
                  ['image','video','audio']]
    
    extensions['media'] = list(chain(*media_exts))

    return extensions  # Accessible dictionary of common extensions
    
def get_exclusions(*exclusion_specs, path_set=None, cache=True,
                   exclude_by_size=False, max_file_size='20MB'):
    """Get a list of file patterns to exclude based on specified criteria.
    
    Args:
        *exclusion_specs: Variable number of exclusion specifications.
            These can be categories like 'image', 'video', 'audio', etc.
        path_set (Union[str, list], optional): Either a directory path or a list of file paths
            to check for exclusions by size. Defaults to None.
        cache (bool, optional): If True, include '.cache' in exclusions. Defaults to True.
        exclude_by_size (bool, optional): If True, exclude files larger than max_file_size.
            Defaults to False.
        max_file_size (str, optional): Maximum file size as a string with unit (e.g., '20MB').
            Defaults to '20MB'.
    
    Returns:
        list: List of file patterns and paths to exclude.
    """
    extensions = _get_extensions()
    
    exclusions = []
    unparsable = []
    
    for exclusion in exclusion_specs:
        if exclusion in extensions:
            exclusions.extend(extensions[exclusion])
            
        else: # append to unparsable
            unparsable.extend(exclusion)

    if cache: exclusions += ['.cache']

    if len(unparsable) >= 1:
        print(f'{unparsable} not in registered exclusions; '+
              f'please choose from one of {list(extensions.keys())}')
            
    # Handle large files
    if exclude_by_size and path_set:
        size_limit = float(max_file_size[:-2])
        if isinstance(path_set, str) and os.path.isdir(path_set):
            for root, dirs, files in os.walk(path_set):
                for name in files:
                    file_path = os.path.join(root, name)
                    if get_file_size(file_path) > size_limit:
                        exclusions.append(file_path)
                        
        elif isinstance(path_set, list):
            for file_path in path_set:
                if get_file_size(file_path) > size_limit:
                    exclusions.append(file_path)

    return exclusions