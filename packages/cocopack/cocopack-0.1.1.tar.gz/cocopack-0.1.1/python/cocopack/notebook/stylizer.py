from os import environ as ENVIRON
from IPython.display import display, HTML

__all__ = ['auto_style', 'is_running_in_jupyter', 'is_running_in_vscode']

def get_jupyter_css(text_only=False, as_style=False, **kwargs):
    """Generate CSS styling for Jupyter outputs.
    
    Parameters
    ----------
    text_only : bool, optional
        If True, return only text-related styles (default False)
    as_style : bool, optional
        If True, return CSS as a formatted string (default False)
    **kwargs : dict
        Additional CSS properties to include
        
    Returns
    -------
    dict or str
        CSS properties as a dictionary or formatted string
        
    Examples
    --------
    >>> css = get_jupyter_css(text_only=True)
    >>> css['font-family']
    'monospace'
    
    >>> css = get_jupyter_css(as_style=True)
    >>> print(css)
    'font-family: monospace; font-size: 13px; ...'
    """
    text_style = {'font-family': 'monospace',
                  'font-weight': 'normal',
                  'font-size': '13px',
                  'line-height': '16px'}
    
    div_style = {'padding-bottom': '0px',
                  'margin-bottom': '0px',
                  'padding-top': '0px',
                  'padding-left': '8px',
                  'margin-right': '-20px'}

    style_dict = {**text_style, **div_style}

    if text_only:
        style_dict = text_style

    for key, value in kwargs.items():
        style_dict[key.replace('_', '-')] = value

    if not as_style:
        return style_dict

    return '; '.join([f'{k}: {v}' for k,v in style_dict.items()])

def load_vscode_styles(style_filepath='auto'):
    """Load VSCode-specific CSS styles for Jupyter outputs.
    
    Parameters
    ----------
    style_filepath : str, optional
        Path to CSS file (default 'auto' uses built-in styles)
        
    Returns
    -------
    None
        Displays styled HTML in Jupyter environment
        
    Examples
    --------
    >>> load_vscode_styles()  # Load default styles
    >>> load_vscode_styles('custom.css')  # Load custom styles
    """
    DIR = '/'.join(__file__.split('/')[:-1])
    
    if style_filepath == 'auto':
        style_filepath = f'{DIR}/vscode.css'
        
    with open(style_filepath, 'r') as file:
        css_inject = file.read()
        
    init_msg = 'Jupyter styling updated for VSCode'
    
    text_css = get_jupyter_css(text_only=True, 
                              as_style=True,
                              font_size='12px')
        
    display(HTML(f"<style type='text/css'>{css_inject}</style>"+
                f"<span style='{text_css}'>{init_msg}</span>"))
    
def is_running_in_jupyter():
    try: # check for running IPyKernelApp
        from IPython import get_ipython
        return "IPKernelApp" in get_ipython().config
    except (ImportError, AttributeError):
        return False
    
def is_running_in_vscode():
    return any('VSCODE' in var for var in ENVIRON)

def is_running_in_vscode_jupyter():
    return is_running_in_vscode() and is_running_in_jupyter()
    
def auto_style(verbose=False):
    
    if is_running_in_vscode_jupyter():
        return load_vscode_styles()
            
    else: # message if verbose
        if verbose:
            print('No IDE-specific styling added.')