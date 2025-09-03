"""
Configuration settings for the PDF parser.

This module loads configuration from environment variables or default values.
"""

import os
import logging
from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "models"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output"))
DEBUG_DIR = os.getenv("DEBUG_DIR", os.path.join(OUTPUT_DIR, "debug"))
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(BASE_DIR, "temp"))

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok = True)
os.makedirs(OUTPUT_DIR, exist_ok = True)
os.makedirs(TEMP_DIR, exist_ok = True)

# Model paths
YOLO_MODEL_PATH = os.path.join(MODEL_DIR, "doclayout_yolo_docstructbench_imgsz1024.pt")

# Image Processing Settings
ZOOM_FACTOR = float(os.getenv("ZOOM_FACTOR", "2.0"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))
CONTAINMENT_THRESHOLD = float(os.getenv("CONTAINMENT_THRESHOLD", "0.90"))

# Box Processing Settings
AUTOMATIC_ROW_DETECTION = os.getenv("AUTOMATIC_ROW_DETECTION", "True").lower() in ("true", "1", "yes")
ROW_SIMILARITY_THRESHOLD = int(os.getenv("ROW_SIMILARITY_THRESHOLD", "10"))
CONTAINER_THRESHOLD = int(os.getenv("CONTAINER_THRESHOLD", "2"))

# Memory Management Settings
MEMORY_EFFICIENT = os.getenv("MEMORY_EFFICIENT", "True").lower() in ("true", "1", "yes")
PAGE_BATCH_SIZE = int(os.getenv("PAGE_BATCH_SIZE", "1"))
ENABLE_GC = os.getenv("ENABLE_GC", "True").lower() in ("true", "1", "yes")
CLEAR_CUDA_CACHE = os.getenv("CLEAR_CUDA_CACHE", "True").lower() in ("true", "1", "yes")

# Text label categories (elements that should be preserved during processing)
TEXT_LABELS = ["title", "plain_text"] #"table_caption", "table_footnote", "formula_caption"]

# Embedding Settings
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

# Debug mode settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
if DEBUG_MODE:
    logging.basicConfig(level = logging.DEBUG)

else:
    logging.basicConfig(level = logging.INFO)

# System prompt for table classification
SYSTEM_PROMPT = """
You are a PDF-table classifier.  
Your entire reply **MUST be a single, valid JSON object** that uses the exact keys and formats shown below.

[INPUT]
  [TABLE_TEXT] - raw text of the extracted table  
  [CATEGORIES] - a JSON/dict mapping each category name to its natural-language description.
                 e.g. {"change_table": "If the table represents a change or amendment to existing products, goods, or services", "contact_information": "If the table contains contact information for a person or company", ...}

[TASK]
  For **each** category in [CATEGORIES] decide whether the table satisfies the description (**true**) or not (**false**).

[OUTPUT]
  Return **ONLY** minified JSON with the same keys that appear in [CATEGORIES], 
  e.g.: {"change_table": true, "contact_information": false, ...}

[RULES]
  - Use **only** the category names provided in [CATEGORIES] as JSON keys.  
  - Values **must** be lowercase JSON booleans: `true` or `false`.  
  - **Never** add keys, comments, or extra text.  
  - If uncertain, output `false`.  
  - Think step-by-step **internally**, but output **only** the JSON object.  
  - The result **must parse** with a standard JSON parser.
"""

TABLE_CATEGORIES = {"summary": "A brief summary with the content summary being less than 50 words about the content in the table.",
                    "address_information": "If the table contains address information like shipping address, billing address, vendor address, or customer address",
                    "billing_information": "If the table contains billing instructions such as payment instructions, payment frequency, or billed to instructions",
                    "change_table": "If the table represents a change or amendment to existing products, goods, or services",
                    "contact_information": "If the table contains contact information for a person or company",
                    "date_information": "If the table contains commitment period information such as start and end dates, contract term, or auto-renewal information. Do not include dates related to signatures or individual products, goods, or services",
                    "discount_inforation": "If the table content explicit information about discounts. Only answer True if there is content explicitly stating discounts. If a product, good, or service has no cost information return False unless the lack of cost information is labeled as a discount in the table",
                    "overview_information": "If the table is primarily an overview, description, or summary of the document or section",
                    "product_table": "If the table an image of products, goods, or services from a purchase order",
                    "signature_information": "If the content is a signature table",
                    "terms_information": "If the content is primarily a list of terms such as legal terms, definitions, or price increase terms",
                    "totals": "If the content represents billing or cost totals",
                    "charges_recurring": "Tables that list ongoing/periodic charges (e.g., 'Monthly Recurring Services', lines with an MRC column or recurring rate). Do not use for one-time fees.",
                    "charges_one_time": "Tables that list setup/installation or other non-recurring items (NRC or 'One-Time Items').",
                    "line_item_pricing": "General line-item price tables showing Qty/UoM, unit rate, and extended price (often with both MRC and NRC columns). Use when the table is not explicitly scoped to recurring-only or one-time-only.",
                    "taxes_and_fees": "Tables that explicitly enumerate regulatory or compliance surcharges, taxes, or fees (e.g., e911, administrative recovery)."}