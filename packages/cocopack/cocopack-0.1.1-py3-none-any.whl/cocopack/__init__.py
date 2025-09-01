__version__ = "0.1.0"

from . import notebook

from os import environ

if not environ.get('ZERO_STYLE', False):
    notebook.stylizer.auto_style()
    
from .figure_ops import (
    slides_to_images,
    convert_to_pdf,
    convert_images_to_pdf,
    mogrify_images_to_pdf,
)

from .notebook import (
    set_autoreload,
)

from .shellpack import (
    shell_commands,
    install_shell_scripts,
)

from . import shellpack as shell

__all__ = [
    # from figure_ops
    'slides_to_images',
    'convert_to_pdf',
    'convert_images_to_pdf',
    'mogrify_images_to_pdf',
    
    # from notebook
    'set_autoreload',
    
    # from shellpack
    'shell_commands',
    'install_shell_scripts',
]