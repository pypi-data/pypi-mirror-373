from IPython import get_ipython
    
def set_autoreload(level='complete'):
    """Configure IPython's autoreload extension with specified level.
    
    This function configures IPython's autoreload extension to automatically reload
    Python modules before executing code. This is useful during development to see
    changes to imported modules without restarting the kernel.
    
    Parameters
    ----------
    level : str, optional
        The autoreload level to set. Options are:
        - 'off': Disable autoreload
        - 'light': Reload only modules imported with %aimport
        - 'complete': Automatically reload all modules (default)
        
    Returns
    -------
    None
    
    Examples
    --------
    >>> from cocopack import notebook
    >>> notebook.set_autoreload('complete') # Enable full autoreload
    >>> notebook.set_autoreload('off')  # Disable autoreload
    
    Notes
    -----
    This function must be run in an IPython environment (e.g., Jupyter notebook).
    It will raise an EnvironmentError if run in a standard Python interpreter.
    """
    # Define the mapping between string levels and their numeric equivalents
    levels = {'off': 0, 'light': 1, 'complete': 2}

    # Convert string levels to their numeric equivalents if necessary
    if isinstance(level, str):
        level = levels.get(level.lower(), 2)  # Default to 'complete' if not found

    # Get the IPython interactive shell instance
    ip = get_ipython()
    if ip is None:
        raise EnvironmentError("This function can only be run inside an IPython environment.")

    # Load the autoreload extension if it's not already loaded
    if 'autoreload' not in ip.extension_manager.loaded:
        ip.run_line_magic('reload_ext', 'autoreload')

    elif 'autoreload' in ip.extension_manager.loaded:
        ip.run_line_magic('reload_ext', 'autoreload')

    # Always set the autoreload level to the specified level
    ip.run_line_magic('autoreload', str(level))