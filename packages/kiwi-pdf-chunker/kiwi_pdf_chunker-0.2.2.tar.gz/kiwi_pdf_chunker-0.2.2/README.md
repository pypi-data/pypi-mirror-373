# PDF Parser

A Python package for parsing PDF document layouts using YOLO models, chunking content based on layout, and optionally performing OCR.

## Features

- Convert PDF documents to images for processing.
- Detect document layout elements (e.g., paragraphs, tables, figures) using YOLO.
- Process and refine bounding boxes.
- Chunk document content based on detected layout.
- **(Optional)** Perform OCR on detected elements using Azure Document Intelligence.
- Save structured document data (layouts, chunks, OCR text) in JSON format.
- Get paragraph embeddings using OpenAI embedder 

## Installation

### Prerequisites

- Python 3.10+
- Pip package manager
- (Optional but Recommended) CUDA-capable GPU for YOLO model inference acceleration.

### Steps

1.  **Install the Package:**
    ```bash
    # pip install kiwi-pdf-chunker
    ```

## User-Provided Data

This package requires the user to provide certain data externally:

1.  **Input Directory (`input/`):** Place the PDF documents you want to process in a directory (e.g., `input/`). You will need to provide the path to your input file(s) when using the package.
2.  **Models Directory (`models/`):** Download the necessary YOLO model(s) (e.g., `doclayout_yolo_docstructbench_imgsz1024.pt`) and place them in a dedicated directory (e.g., `models/`). The path to this directory (or the specific model file) will be needed by the parser.