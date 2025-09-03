"""
PDF processing module.

This module contains functions for processing PDF documents, including
converting PDFs to images.
"""

import io
import gc
import logging
from PIL import Image
import fitz  # PyMuPDF
from typing import Dict, Tuple, List

from .config import ZOOM_FACTOR

# Configure logging
logger = logging.getLogger(__name__)

def pdf_to_images(pdf_path: str, dpi: int = 200) -> Tuple[Dict[int, Image.Image], Dict[int, float]]:
    """
    Converts each page of a PDF file to a high-resolution image and calculates scaling factors.

    Args:
        pdf_path (str): The path to the PDF file.
        dpi (int): The resolution (dots per inch) for the output images.

    Returns:
        Tuple containing:
        - A dictionary mapping page numbers (0-indexed) to PIL Image objects.
        - A dictionary mapping page numbers (0-indexed) to the scaling factor used for that page.
    """
    images = {}
    scale_factors = {}
    
    try:
        doc = fitz.open(pdf_path)
        
        for i, page in enumerate(doc):
            # Calculate the scaling factor based on the desired DPI
            # The matrix zooms by dpi/72 because PDF points are 1/72 inch.
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # Get the pixmap (image) of the page
            pix = page.get_pixmap(matrix=mat)
            
            # Convert the pixmap to a PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images[i] = image
            
            # Calculate the precise scaling factor for coordinate conversion
            # This is image pixel width / PDF point width
            pdf_width_points = page.rect.width
            if pdf_width_points > 0:
                scale_factors[i] = pix.width / pdf_width_points
            else:
                scale_factors[i] = zoom # Fallback to the zoom factor

            logger.info(f"Converted page {i} to image ({pix.width}x{pix.height}) with scale factor {scale_factors[i]:.2f}.")

        doc.close()
        
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise

    return images, scale_factors

def pdf_to_images_batched(pdf_path, page_numbers=None, zoom=None): 

    """
    Reads specific pages from a PDF file and converts them into high-resolution PIL Images.
    This function is memory-efficient for processing large PDFs.

    Args:
        pdf_path (str): The file path to the PDF.
        page_numbers (list, optional): List of page numbers to convert (1-indexed).
            If None, all pages will be converted.
        zoom (float, optional): Scaling factor for the image resolution.
            Defaults to the value in config.

    Returns:
        dict: A dictionary where keys are page numbers (1-indexed) and values are
            high-resolution PIL Images.
    """

    if zoom is None:
        zoom = ZOOM_FACTOR

    images = {}
    try:
        pdf_document = fitz.open(pdf_path)  # Open the PDF file
        
        # If no specific pages are requested, convert all pages
        if page_numbers is None:
            page_numbers = list(range(1, len(pdf_document) + 1))
            
        # Convert only the requested pages
        for page_number in page_numbers:

            if page_number < 1 or page_number > len(pdf_document):

                logger.warning(f"Page number {page_number} is out of range (1-{len(pdf_document)})")
                continue
                
            page = pdf_document.load_page(page_number - 1)  # Load page (0-indexed in fitz)
            matrix = fitz.Matrix(zoom, zoom)  # Scale the image for higher resolution
            pixmap = page.get_pixmap(matrix=matrix)  # Render the page to a pixmap

            # Convert pixmap to PIL Image
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            images[page_number] = image  # Store the image in the dictionary
            
            # Free memory
            pixmap = None
            gc.collect()

        pdf_document.close()  # Close the PDF document

    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {str(e)}")

    return images

def get_pdf_page_count(pdf_path): 
    """
    Get the number of pages in a PDF file.
    
    Args:
        pdf_path (str): The file path to the PDF.
        
    Returns:
        int: The number of pages in the PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        page_count = len(pdf_document)
        pdf_document.close()
        return page_count
    except Exception as e:
        logger.error(f"Error getting PDF page count: {str(e)}")
        return 0