"""
Image processing module.

This module contains functions for processing images, including preprocessing
for OCR and annotating images with detected elements.
"""

import os
import cv2
import logging
import numpy as np
from .box_processing import get_box_class
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logger = logging.getLogger(__name__)

# Define colors for different element types
CLASS_COLORS = {'plain_text': (255, 0, 0),      # Red
                'title': (0, 0, 255),           # Blue
                'table': (0, 255, 0),           # Green
                'table_caption': (255, 165, 0), # Orange
                'figure': (128, 0, 128),        # Purple
                'formula': (255, 192, 203),     # Pink
                'list': (165, 42, 42),          # Brown
                'default': (128, 128, 128)}     # Gray for unknown types

def preprocess_image(img): 

    """
    Pre-processes the image to improve OCR quality.

    Args:
        img (PIL.Image): The input image.

    Returns:
        PIL.Image: The pre-processed image.
    """

    # Convert image to grayscale
    img = img.convert('L')

    # Convert to numpy array for OpenCV processing
    img_np = np.array(img)

    # Apply Gaussian Blur
    img_np = cv2.GaussianBlur(img_np, (5, 5), 0)

    # Apply adaptive thresholding
    img_np = cv2.adaptiveThreshold(
        img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Convert back to PIL image
    preprocessed_img = Image.fromarray(img_np)

    return preprocessed_img

def get_color_for_class(class_name): 

    """
    Get a consistent color for a class type.
    
    Args:
        class_name (str): The class name to get a color for.
        
    Returns:
        tuple: RGB color tuple.
    """

    # Look for partial matches in the CLASS_COLORS dictionary
    for key, color in CLASS_COLORS.items():
        if key in class_name:
            return color
    
    # Return default color if no match found
    return CLASS_COLORS['default']

def annotate_image(detections, original_image):

    """
    Annotate the original image with bounding boxes and labels.

    Args:
        detections (dict): Dictionary of detected elements with their bounding boxes.
        original_image (PIL.Image): The original image to annotate.

    Returns:
        PIL.Image: The annotated image with bounding boxes and labels.
    """

    annotated_image = original_image.copy()
    draw = ImageDraw.Draw(annotated_image)
    
    # Try to load a font, fall back to default if not available
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    
    except IOError:
       
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 15)
       
        except IOError:
            font = ImageFont.load_default()

    for label, data in detections.items():
      
        x, y, w, h = data['coordinates']
        class_name = get_box_class(label)
        color = get_color_for_class(class_name)
        
        # Convert RGB color to string format '#RRGGBB'
        color_str = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
        
        # Draw rectangle
        draw.rectangle([x, y, x + w, y + h], outline=color_str, width=2)
        
        # Draw label background for better visibility
        text_bbox = draw.textbbox((x, y - 15), label, font=font)
        draw.rectangle([text_bbox[0]-5, text_bbox[1]-2, text_bbox[2]+5, text_bbox[3]+2], 
                       fill=color_str)
        
        # Draw label text in contrasting color
        text_color = '#FFFFFF'  # White for dark backgrounds
        if sum(color) > 500:  # If background color is light
            text_color = '#000000'  # Use black text
            
        draw.text((x, y - 15), label, fill=text_color, font=font)

    return annotated_image

def save_annotated_image(annotated_image, output_path, page_number): 

    """
    Save an annotated image to disk.

    Args:
        annotated_image (PIL.Image): The annotated image.
        output_path (str): The base output directory.
        page_number (int): The page number to include in the filename.

    Returns:
        str: The path to the saved image.
    """

    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, f"page_{page_number}_annotated.png")
    annotated_image.save(file_path)
    logger.info(f"Saved annotated image to {file_path}")

    return file_path

def analyze_image_density(image, block_size=50): 

    """
    Analyze the text density of an image to identify potential text regions.
    
    Args:
        image (PIL.Image): The input image
        block_size (int, optional): Size of blocks for density analysis. Defaults to 50.
        
    Returns:
        numpy.ndarray: Density map indicating likelihood of text presence
    """

    # Convert to grayscale
    gray_image = image.convert('L')
    np_image = np.array(gray_image)
    
    # Initialize density map
    height, width = np_image.shape
    density_map = np.zeros((height // block_size + 1, width // block_size + 1))
    
    # Apply edge detection to highlight text
    edges = cv2.Canny(np_image, 100, 200)
    
    # Calculate density in each block
    for y in range(0, height, block_size):

        for x in range(0, width, block_size):

            block = edges[y:min(y+block_size, height), x:min(x+block_size, width)]
            density = np.sum(block > 0) / (block_size * block_size)
            density_map[y // block_size, x // block_size] = density
    
    return density_map

def find_potential_text_regions(image, density_threshold=0.1):
    """
    Find potential text regions based on image density analysis.
    
    Args:
        image (PIL.Image): The input image
        density_threshold (float, optional): Threshold for considering a region as text.
            Defaults to 0.1.
    
    Returns:
        list: List of bounding boxes [x, y, w, h] for potential text regions
    """
    # Get density map
    density_map = analyze_image_density(image)
    
    # Find connected regions above threshold
    binary_map = density_map > density_threshold
    
    # Label connected components
    num_labels, labels = cv2.connectedComponents(binary_map.astype(np.uint8))
    
    # Extract bounding boxes for each component
    boxes = []
    for label in range(1, num_labels):
        points = np.argwhere(labels == label)
        if len(points) < 3:  # Skip very small components
            continue
            
        # Convert back to original image coordinates
        block_size = 50
        y_min, x_min = points.min(axis=0) * block_size
        y_max, x_max = (points.max(axis=0) + 1) * block_size
        
        boxes.append([x_min, y_min, x_max - x_min, y_max - y_min])
    
    return boxes