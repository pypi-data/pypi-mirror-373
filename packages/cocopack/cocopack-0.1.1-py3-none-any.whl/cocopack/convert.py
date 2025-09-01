import os

from copy import copy
from PIL import Image

__all__ = ['convert_image']

# Input / Image Conversion ----------------------------------------

def _make_opaque(img_input, bg_color=(255, 255, 255)):
    # if input is path, load it as image
    if isinstance(img_input, str):
        img = Image.open(img_input)
        
    else: # assume input is image
        img = copy(img_input)
    
    # Check if the image has an alpha channel
    if img.mode in ('RGBA', 'LA') or ('transparency' in img.info):
        # Create a new image with a white background
        background = Image.new(img.mode[:-1], img.size, bg_color)
        # Paste the image on the background (masking with itself)
        background.paste(img, img.split()[-1])
        image = background  # ... using the alpha channel as mask
    
    # Convert image to RGB 
    if img.mode != 'RGB':
        img = img.convert('RGB')
            
    return img # image updated with nontrasparent background

def convert_image(source_path, target_format, **kwargs):
    """Convert an image file to another format.
    
    Args:
        source_path (str): Path to the source image file.
        target_format (str): Target format to convert to (e.g., 'jpg', 'png', 'pdf').
        **kwargs: Additional keyword arguments.
            remove_original (bool): Whether to remove the original file. Defaults to True.
            
    Returns:
        str: Path to the converted image file.
    """
    # Ensure the target format does not start with a dot
    if target_format.startswith('.'):
        target_format = target_format[1:]
    
    # Load the image with PIL:
    img = Image.open(source_path)
    
    if target_format in ['jpg', 'pdf']:
        img = _make_opaque(img)
    
    # Define the new filename
    base = os.path.splitext(source_path)[0]
    target_path = f"{base}.{target_format.lower()}"
    
    # Convert and save the image
    img.save(target_path, target_format.upper())
    
    if kwargs.pop('remove_original', True):
        os.remove(source_path)

    return target_path # return the new path