"""
Model initialization and management module.

This module handles the initialization and loading of ML models used for
document parsing and OCR.
"""

import os
import logging
import torch
from .config import YOLO_MODEL_PATH, MODEL_DIR

# Configure logging
logger = logging.getLogger(__name__)

def initialize_yolo_model(model_path=None): 

    """
    Initialize the YOLO model for document layout detection.
    
    Args:
        model_path (str, optional): Path to the YOLO model file.
            Defaults to the path in config.
    
    Returns:
        The initialized YOLO model.
    """ 

    try:
        
        # If model_path not provided, use default from config
        if model_path is None:
            model_path = YOLO_MODEL_PATH
            
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"YOLO model not found at {model_path}. "
                f"Please download the model to the models directory."
            )
            
        # Import here to avoid loading at module level
        from doclayout_yolo import YOLOv10
        
        # Clear any existing CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Determine device (CUDA or CPU)
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        # Initialize model
        model = YOLOv10(model_path)
        logger.info(f"YOLO model loaded successfully. Using device: {device}")
        
        return model
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize YOLO model: {str(e)}")

def download_models(force=False): 

    """
    Ensure all required models are downloaded and available.
    
    Args:
        force (bool, optional): If True, force re-download even if models exist.
            Defaults to False.
    """

    # Create model directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Check YOLO model
    if not os.path.exists(YOLO_MODEL_PATH) or force:
        try:
            # This would be where you'd implement the download logic
            # For now, just print an instructional message
            logger.warning(f"YOLO model not found at {YOLO_MODEL_PATH}")
            logger.warning("Please download the model manually and place it in the models directory.")
            logger.warning("Model name should be: doclayout_yolo_docstructbench_imgsz1024.pt")
        except Exception as e:
            logger.error(f"Error downloading YOLO model: {str(e)}")
    
    # PaddleOCR will download its models automatically when initialized