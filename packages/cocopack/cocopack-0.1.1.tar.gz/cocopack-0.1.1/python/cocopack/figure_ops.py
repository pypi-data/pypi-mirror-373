import os, re
import glob
import subprocess
import platform
from copy import copy
from PIL import Image, ImageChops

__all__ = [
    'slides_to_images',
    'convert_to_pdf',
    'convert_images_to_pdf',
    'mogrify_images_to_pdf',
]

# Core Functions ------------------------------------------------------------

def slides_to_images(input_path, output_path, filename_format='figure{:01d}.png',
                     crop_images=True, margin_size='1cm', dpi=300):
    """Convert presentation slides to image files.
    
    Args:
        input_path (str): Path to the presentation file (.ppt, .pptx, or .key).
        output_path (str): Directory path where the images will be saved.
        filename_format (str, optional): Format string for the output filenames. Defaults to 'figure{:01d}.png'.
        crop_images (bool, optional): Whether to crop whitespace around images. Defaults to True.
        margin_size (str, optional): Margin size to add around cropped images. Defaults to '1cm'.
        dpi (int, optional): DPI for the output images. Defaults to 300.
    """
    input_ext = _check_slides_extension(input_path)

    if input_ext in ['.ppt', '.pptx']:
        powerpoint_to_images(input_path, output_path, filename_format)

    if input_ext == '.key':
        keynote_to_images(input_path, output_path, filename_format)

    if crop_images:
        crop_whitespace(output_path, margin_size=margin_size, dpi=dpi)

def keynote_to_images(input_path, output_path, filename_format='figure{:01d}.png'):
    """Convert Keynote slides to image files using AppleScript.
    
    Args:
        input_path (str): Path to the Keynote file.
        output_path (str): Directory path where the images will be saved.
        filename_format (str, optional): Format string for the output filenames. Defaults to 'figure{:01d}.png'.
    
    Note:
        This function only works on macOS systems with Keynote installed.
        Source: https://iworkautomation.com/keynote/document-export.html
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    applescript = f'''
    tell application "Keynote"
        set theDocument to open "{input_path}"
        set documentName to the name of theDocument
        set targetFolderHFSPath to POSIX file "{output_path}" as string

        export theDocument as slide images to file targetFolderHFSPath with properties {{image format:PNG, skipped slides:FALSE}}
    end tell
    '''
    
    subprocess.run(['osascript', '-e', applescript])

    if filename_format:
        reformat_image_filenames(output_path, filename_format)

def powerpoint_to_images(input_path, output_path, filename_format='figure{:01d}.png'):
    """Convert PowerPoint slides to image files.
    
    Args:
        input_path (str): Path to the PowerPoint file (.ppt or .pptx).
        output_path (str): Directory path where the images will be saved.
        filename_format (str, optional): Format string for the output filenames. Defaults to 'figure{:01d}.png'.
    
    Note:
        This function uses different methods depending on the operating system:
        - On macOS: Uses AppleScript with PowerPoint
        - On Windows: Uses win32com.client
        - On other platforms: Attempts to use LibreOffice or python-pptx
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    if platform.system() == 'Darwin':  # macOS
        applescript = f'''
        tell application "Microsoft PowerPoint"
            open "{input_path}"
            set thePresentation to active presentation
            
            set slideCount to count of slides in thePresentation
            repeat with i from 1 to slideCount
                set current slide of thePresentation to slide i of thePresentation
                set slideFile to "{output_path}/Slide" & i & ".png"
                save thePresentation in slideFile as save as PNG
            end repeat
            
            close thePresentation saving no
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript])
    
    elif platform.system() == 'Windows':
        try:
            import win32com.client
            
            # Initialize PowerPoint application
            ppt = win32com.client.Dispatch("PowerPoint.Application")
            ppt.Visible = True
            
            # Open the presentation
            presentation = ppt.Presentations.Open(input_path)
            
            # Export slides as images
            for i in range(1, presentation.Slides.Count + 1):
                slide_path = os.path.join(output_path, f"Slide{i}.png")
                presentation.Slides(i).Export(slide_path, "PNG")
            
            # Close presentation without saving changes
            presentation.Close()
            ppt.Quit()
            
        except ImportError:
            print("Error: win32com is required for Windows. Install with 'pip install pywin32'")
            return
        except Exception as e:
            print(f"Error exporting PowerPoint slides: {e}")
            return
    
    else:
        try:
            from pptx import Presentation
            
            # This is a limited fallback as python-pptx doesn't directly support exporting slides as images
            # For full functionality, consider using LibreOffice CLI in a subprocess
            print("Using python-pptx for basic PowerPoint handling. For full slide export, use Windows or macOS.")
            
            # For Linux/other platforms, can use LibreOffice command line:
            # subprocess.run(['soffice', '--headless', '--convert-to', 'png', '--outdir', output_path, input_path])
            
            # Example LibreOffice conversion (uncomment if LibreOffice is available)
            libreoffice_cmd = ['soffice', '--headless', '--convert-to', 'png', '--outdir', output_path, input_path]
            try:
                subprocess.run(libreoffice_cmd, check=True)
            except subprocess.CalledProcessError:
                print("Warning: LibreOffice conversion failed. Limited functionality available.")
                print("Install LibreOffice for better platform-independent conversion.")
            
        except ImportError:
            print("Error: pptx package is required. Install with 'pip install python-pptx'")
            return
    
    if filename_format:
        reformat_image_filenames(output_path, filename_format)

# Helper Functions ------------------------------------------------------------

def _check_slides_extension(input_path):
    input_ext = os.path.splitext(input_path)[1]

    if input_ext not in ['.key', '.ppt', '.pptx']:
        raise ValueError(f"Unsupported file extension: {input_ext}",
                         "Supported extensions: .key, .ppt, .pptx")
    
    return input_ext

def reformat_image_filenames(output_path, reformat_pattern):
    """Rename image files based on a specified pattern.
    
    Args:
        output_path (str): Directory containing the image files.
        reformat_pattern (str): Format string for the new filenames (e.g., 'figure{:01d}.png').
            The format string should contain a placeholder for the slide number.
    """
    image_files = glob.glob(os.path.join(output_path, '*.png'))
    
    for image_file in image_files:
        basename = os.path.basename(image_file)
        slide_number = re.search(r'\d+', basename).group(0)
        new_filename = reformat_pattern.format(int(slide_number))
        new_filepath = os.path.join(output_path, new_filename)
        os.rename(image_file, new_filepath)

def crop_whitespace(image_path, output_path=None, margin_size='1cm', dpi=300):
    """Crop whitespace around images and add a specified margin.
    
    Args:
        image_path (str): Path to an image file or a directory containing image files.
        output_path (str, optional): Path where the cropped images will be saved. 
            If None, overwrites the original files. Defaults to None.
        margin_size (str, optional): Margin size to add around cropped images in cm. Defaults to '1cm'.
        dpi (int, optional): DPI for the output images, used for margin calculation. Defaults to 300.
    """
    def add_margin(image, margin_pixels):
        width, height = image.size
        new_width = width + 2 * margin_pixels
        new_height = height + 2 * margin_pixels
        new_image = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
        new_image.paste(image, (margin_pixels, margin_pixels))
        return new_image

    def crop_single_image(source_file, output_file):
        image = Image.open(source_file)
        image = image.convert("RGBA")

        # Remove alpha channel by pasting the image onto a white background
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image_rgb = background.convert("RGB")

        # Find the bounding box and crop the image
        difference = ImageChops.difference(image_rgb, Image.new("RGB", image.size, (255, 255, 255)))
        bounds = difference.getbbox()
        cropped_image = image.crop(bounds)

        # Add margin if specified
        if margin_size:
            margin_cm = float(margin_size.strip('cm'))
            margin_pixels = int(margin_cm * dpi / 2.54)  # Convert cm to pixels
            cropped_image = add_margin(cropped_image, margin_pixels)

        cropped_image.save(output_file)

    if os.path.isdir(image_path):
        for filename in os.listdir(image_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                source_file = os.path.join(image_path, filename)
                if output_path:
                    output_file = os.path.join(output_path, filename)
                else:
                    output_file = source_file
                crop_single_image(source_file, output_file)
    else:
        if output_path is None:
            output_path = image_path
        crop_single_image(image_path, output_path)

def convert_to_pdf(image_path, output_path=None, dpi=300, **kwargs):
    """Convert {PNG, JPEG, TIFF} images to high-quality PDF files.
    
    Args:
        image_path (str): Path to an image file or a directory containing image files.
        output_path (str, optional): Path where the PDF files will be saved.
            If None, uses the same location as the input. Defaults to None.
        dpi (int, optional): DPI for the output PDF files. Defaults to 300.
        **kwargs: Additional keyword arguments.
            pdf_only (bool): If True, removes the original image files. Defaults to False.
    
    Returns:
        None
    """
    if output_path is None:
        output_path = copy(image_path)
    
    if os.path.isdir(image_path):
        for filename in os.listdir(image_path):
            if filename.lower().endswith('.png', '.jpg', '.jpeg', '.tiff', '.tif'):
                source_file = os.path.join(image_path, filename)
                output_file = os.path.join(output_path, os.path.splitext(filename)[0] + '.pdf')
                print(f'Converting {source_file} to {output_file}...')
                image = Image.open(source_file)
                # Convert to RGB mode if necessary
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                image.save(output_file, 'PDF', resolution=dpi)
    else:
        output_file = os.path.splitext(output_path)[0] + '.pdf'
        image = Image.open(image_path)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        image.save(output_file, 'PDF', resolution=dpi)

    if kwargs.get('pdf_only', False):
        os.remove(image_path)

def convert_images_to_pdf(input_path, dpi=300, **kwargs):
    """Convert all {PNG, JPEG, TIFF} images in a directory and its subdirectories to PDF files.
    
    Args:
        input_path (str): Path to the directory containing {PNG, JPEG, TIFF} images.
        dpi (int, optional): DPI for the output PDF files. Defaults to 300.
        **kwargs: Additional keyword arguments passed to convert_to_pdf.
            pdf_only (bool): If True, removes the original image files. Defaults to False.
    """
    image_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.tif']
    image_files = glob.glob(os.path.join(input_path, f'**/*.{",".join(image_exts)}'), recursive=True)
    for image_file in image_files:
        convert_to_pdf(image_file, None, dpi, **kwargs)

def mogrify_images_to_pdf(input_path, **kwargs):
    """Convert {PNG, JPEG, TIFF} images to PDF using ImageMagick's mogrify command.
    
    Args:
        input_path (str): Path to the directory containing {PNG, JPEG, TIFF} images.
        **kwargs: Additional keyword arguments.
            pdf_only (bool): If True, removes the original image files. Defaults to False.
            
    Note:
        This function requires ImageMagick to be installed on the system.
    """
    image_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.tif']
    image_files = glob.glob(os.path.join(input_path, f'**/*.{",".join(image_exts)}'), recursive=True)
    for image_file in image_files:
        subprocess.run(['mogrify', '-format', 'pdf', '-quality', '100', '-density', '300', image_file])

    if kwargs.get('pdf_only', False):
        for image_file in image_files:
            os.remove(image_file)
