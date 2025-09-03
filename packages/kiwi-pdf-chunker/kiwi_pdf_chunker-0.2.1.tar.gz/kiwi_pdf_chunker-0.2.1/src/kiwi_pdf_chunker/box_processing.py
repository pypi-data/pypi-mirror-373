"""
Bounding box processing module.

This module contains functions for processing bounding boxes from document layout detection,
including merging overlapping boxes and sorting them.
"""

from PIL import Image
import logging
import json
import os
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def iou(box1, box2): 

    """
    Compute Intersection over Union (IoU) between two bounding boxes.

    Args:
        box1 (list): First bounding box coordinates [x, y, w, h].
        box2 (list): Second bounding box coordinates [x, y, w, h].

    Returns:
        float: The IoU value between 0 and 1.
    """

    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Convert width and height to bottom-right corner coordinates
    x1_br, y1_br = x1 + w1, y1 + h1
    x2_br, y2_br = x2 + w2, y2 + h2

    # Compute intersection coordinates
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1_br, x2_br)
    inter_y2 = min(y1_br, y2_br)

    # Compute intersection area
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    # Compute union area
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area

    # Compute IoU
    if union_area == 0:
        return 0

    return inter_area / union_area

def containment_ratio(box1, box2): 

    """
    Compute containment ratio of box1 inside box2.
    This measures what percentage of box1 is contained within box2.

    Args:
        box1 (list): First bounding box coordinates [x, y, w, h] (the potentially contained box).
        box2 (list): Second bounding box coordinates [x, y, w, h] (the potentially containing box).

    Returns:
        float: The containment ratio between 0 and 1. 1 means box1 is completely inside box2.
    """

    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Convert width and height to bottom-right corner coordinates
    x1_br, y1_br = x1 + w1, y1 + h1
    x2_br, y2_br = x2 + w2, y2 + h2

    # Compute intersection coordinates
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1_br, x2_br)
    inter_y2 = min(y1_br, y2_br)

    # Compute intersection area
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    # Compute box1 area
    box1_area = w1 * h1

    # Compute containment ratio (what percentage of box1 is inside box2)
    if box1_area == 0:
        return 0

    return inter_area / box1_area

def merge_boxes(box1, box2): 

    """
    Merge two bounding boxes into one larger bounding box.

    Args:
        box1 (list): First bounding box coordinates [x, y, w, h].
        box2 (list): Second bounding box coordinates [x, y, w, h].

    Returns:
        list: The merged bounding box coordinates [x, y, w, h].
    """

    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Compute new bounding box coordinates
    x_min = min(x1, x2)
    y_min = min(y1, y2)

    x_max = max(x1 + w1, x2 + w2)
    y_max = max(y1 + h1, y2 + h2)

    return [x_min, y_min, x_max - x_min, y_max - y_min]

def get_box_class(key):
    """
    Extract the class name from a box key.
    
    Args:
        key (str): The box key (e.g., 'plain_text_0', 'title_1').
        
    Returns:
        str: The class name (e.g., 'plain_text', 'title').
    """
    if '_' in key:
        return key.rsplit('_', 1)[0]
    return key

def nms_merge_boxes(detections, iou_threshold=0.45, class_specific=True):
    
    """
    Apply Non-Maximum Suppression (NMS) to merge overlapping bounding boxes.

    Args:
        detections (dict): Dictionary of detected elements with their bounding boxes.

        iou_threshold (float, optional): The IoU threshold for merging boxes. 
            Defaults to 0.45.
        
        class_specific (bool, optional): Whether to only merge boxes of the same class.
            Defaults to True.

    Returns:
        dict: Dictionary with merged bounding boxes.
    """

    # Group boxes by class if class_specific is True
    if class_specific:

        class_groups = {}
        for key, value in detections.items():
            class_name = get_box_class(key)

            if class_name not in class_groups:
                class_groups[class_name] = {}

            class_groups[class_name][key] = value
            
        # Process each class group separately
        merged_detections = {}
        for class_name, group in class_groups.items():

            class_merged = nms_merge_boxes_group(group, iou_threshold)
            merged_detections.update(class_merged)

        return merged_detections
    
    else:

        # Process all boxes together
        return nms_merge_boxes_group(detections, iou_threshold)

def nms_merge_boxes_group(detections, iou_threshold=0.45):

    """
    Apply Non-Maximum Suppression (NMS) to a group of boxes.
    
    Args:
        detections (dict): Dictionary of detected elements with their bounding boxes.
        iou_threshold (float, optional): The IoU threshold for merging boxes.
            Defaults to 0.45.
            
    Returns:
        dict: Dictionary with merged bounding boxes.
    """
    
    boxes = list(detections.items())
    
    # Sort by area (larger boxes first)
    boxes.sort(key=lambda x: x[1]['coordinates'][2] * x[1]['coordinates'][3], reverse=True)  
    merged_detections = {}

    while boxes:
    
        key, top_box = boxes.pop(0)
        top_coords = top_box['coordinates']
        confidence = top_box['confidence']
        merged_boxes = [top_box]

        i = 0
        while i < len(boxes):
    
            other_key, other_box = boxes[i]
    
            if iou(top_coords, other_box['coordinates']) > iou_threshold:
                top_coords = merge_boxes(top_coords, other_box['coordinates'])
                merged_boxes.append(other_box)
                boxes.pop(i)  # Remove merged box from the list
    
            else:
                i += 1

        # Merge images of overlapping boxes
        merged_image = Image.new('RGB', (top_coords[2], top_coords[3]))
        for b in merged_boxes:
    
            rel_x = b['coordinates'][0] - top_coords[0]
            rel_y = b['coordinates'][1] - top_coords[1]
            merged_image.paste(b['image'], (rel_x, rel_y))

        merged_detections[key] = {'coordinates': top_coords, 'image': merged_image, 'confidence': confidence}

    return merged_detections

def remove_container_boxes(detections, min_contained_boxes=2):
   
    """
    Remove boxes that fully contain more than a specified number of other boxes.
    
    This function identifies boxes that appear to be container elements (e.g., sections)
    rather than actual content elements and removes them to reduce overlap.
    
    Args:
        detections (dict): Dictionary of detected elements with their bounding boxes.
        min_contained_boxes (int, optional): Minimum number of contained boxes required
            to consider a box as a container. Defaults to 2.
            
    Returns:
        dict: Dictionary with container boxes removed.
    """

    filtered_detections = detections.copy()
    container_boxes = []
    
    # Count how many boxes are contained within each box
    for key1, box1 in detections.items():
        contained_count = 0
        coords1 = box1['coordinates']
        
        # Skip very small boxes
        if coords1[2] < 10 or coords1[3] < 10:
            continue
        
        for key2, box2 in detections.items():
            if key1 == key2:
                continue
                
            coords2 = box2['coordinates']
            
            # Check if box2 is completely contained within box1
            # A box is contained if all four corners are inside the container box
            x1, y1, w1, h1 = coords1
            x2, y2, w2, h2 = coords2
            
            if (x2 >= x1 and y2 >= y1 and 
                x2 + w2 <= x1 + w1 and y2 + h2 <= y1 + h1):
                contained_count += 1
                
        # If this box contains multiple other boxes, mark it for removal
        if contained_count >= min_contained_boxes:
            container_boxes.append(key1)
            logger.info(f"Marking container box {key1} for removal - contains {contained_count} boxes")
    
    # Remove container boxes
    for key in container_boxes:
        if key in filtered_detections:
            filtered_detections.pop(key)
    
    logger.info(f"Removed {len(container_boxes)} container boxes")

    return filtered_detections

def remove_inner_boxes(detections, containment_threshold=0.95, safe_classes=None):
    """
    Remove boxes that are completely inside another box, with improved handling.

    Args:
        detections (dict): Dictionary of detected elements with their bounding boxes.
        containment_threshold (float, optional): Minimum containment ratio to consider 
            a box as "inside" another box. Defaults to 0.95.
        safe_classes (list, optional): List of class names that should never be removed,
            even if they appear to be inside other boxes. Defaults to None.

    Returns:
        dict: Dictionary with inner boxes removed.
    """
    if safe_classes is None:
        safe_classes = ['plain_text', 'title', 'table_caption']
    
    filtered_detections = detections.copy()
    removed_boxes = []
    
    # Log the initial box count
    logger.info(f"Initial box count: {len(filtered_detections)}")

    # First pass: identify boxes to remove
    for key1, box1 in list(detections.items()):
        x1, y1, w1, h1 = box1['coordinates']
        
        # Skip small boxes (noise)
        if w1 < 10 or h1 < 10:
            filtered_detections.pop(key1, None)
            removed_boxes.append(key1)
            continue
            
        class1 = get_box_class(key1)
        
        # Don't remove boxes of safe classes
        if class1 in safe_classes:
            continue
            
        for key2, box2 in detections.items():
            if key1 == key2:
                continue

            class2 = get_box_class(key2)
                
            # Only remove if the outer box is of a different class
            # (e.g., remove a figure inside a section, but not a paragraph inside a section)
            if class1 == class2:
                continue
                
            # Calculate containment ratio
            cont_ratio = containment_ratio(box1['coordinates'], box2['coordinates'])
            
            # If box1 is mostly inside box2, mark it for removal
            if cont_ratio > containment_threshold:
                # Don't remove if box1 is much smaller than box2 (might be a paragraph in a section)
                area1 = w1 * h1
                x2, y2, w2, h2 = box2['coordinates']
                area2 = w2 * h2
                
                if area1 / area2 < 0.1:  # If box1 is less than 10% of box2's area, keep it
                    logger.info(f"Keeping small box {key1} inside {key2} - containment: {cont_ratio:.2f}, area ratio: {area1/area2:.2f}")
                    continue
                    
                logger.info(f"Removing box {key1} contained in {key2} - containment: {cont_ratio:.2f}")
                filtered_detections.pop(key1, None)
                removed_boxes.append(key1)
                break
    
    # Log the results
    logger.info(f"Removed {len(removed_boxes)} inner boxes")
    logger.info(f"Final box count: {len(filtered_detections)}")
    
    return filtered_detections

def recover_missed_boxes(original_detections, processed_detections, source_image, containment_threshold=0.7):
    
    """
    Attempt to recover boxes that may have been incorrectly removed during processing.
    
    Args:
        original_detections (dict): The original unprocessed detections.
        processed_detections (dict): The processed detections after NMS and inner box removal.
        source_image (PIL.Image): The source image from which detections were made.
        containment_threshold (float, optional): Containment threshold for recovery. Defaults to 0.7.
        
    Returns:
        dict: Updated processed detections with recovered boxes.
    """
    
    recovered_detections = processed_detections.copy()
    recovered_count = 0
    
    # Find boxes that were in original but not in processed
    for key, box in original_detections.items():
        if key in processed_detections:
            continue
            
        class_name = get_box_class(key)
            
        # Check if this box overlaps significantly with any box in processed_detections
        overlapping = False
        for proc_key, proc_box in processed_detections.items():
            proc_class = get_box_class(proc_key)
            
            # Skip checking against boxes of the same class
            if proc_class == class_name:
                continue
                
            # Calculate containment 
            cont_ratio = containment_ratio(box['coordinates'], proc_box['coordinates'])
            
            # If significant overlap but not complete containment, don't recover
            if cont_ratio > 0.2 and cont_ratio < containment_threshold:
                overlapping = True
                break
                
        if not overlapping: 
            
            # This box doesn't overlap with any other box, so recover it
            recovered_detections[key] = box
            recovered_count += 1
            logger.info(f"Recovered box {key} of class {class_name}")
    
    logger.info(f"Recovered {recovered_count} boxes")
    return recovered_detections

def sort_bounding_boxes(boxes_dict, automatic_row_detection=True, y_similarity_threshold=10):
    """
    Sort a dictionary of bounding boxes based on their positions on the page.
    
    Algorithm:
    1. Extract coordinates from each bounding box
    2. If automatic_row_detection is enabled, calculate an appropriate threshold
       based on the distribution of vertical positions
    3. Group boxes into rows based on their vertical positions
    4. Sort boxes within each row by their horizontal positions
    5. Combine sorted rows to create the final ordered dictionary
    
    Args:
        boxes_dict (dict): Dictionary of bounding boxes with coordinates [x, y, width, height]
        automatic_row_detection (bool, optional): If True, automatically determine row grouping.
            Defaults to True.
        y_similarity_threshold (int, optional): Maximum vertical distance to consider boxes
            as being in the same row. Only used if automatic_row_detection is False.
            Defaults to 10 pixels.
    
    Returns:
        dict: A new dictionary with bounding boxes sorted by position (top to bottom, left to right)
    """

    if not boxes_dict:
        return {}
    
    # Extract coordinates for all boxes
    items_with_coords = []
    for key, box_info in boxes_dict.items():
        
        try:
        
            coordinates = box_info.get('coordinates', [0, 0, 0, 0])
            if len(coordinates) < 4:
                continue
                
            x, y, width, height = coordinates
        
            # Use top-left corner as reference
            items_with_coords.append((key, box_info, x, y))
        
        except (TypeError, ValueError):
        
            # Skip items with invalid coordinates
            continue
    
    if not items_with_coords:
        return {}
    
    # Sort items by y-coordinate
    items_sorted_by_y = sorted(items_with_coords, key=lambda item: item[3])

    # Automatic threshold detection
    if automatic_row_detection and len(items_sorted_by_y) > 1:
       
        y_coords = [item[3] for item in items_sorted_by_y]
        y_diffs = [y_coords[i+1] - y_coords[i] for i in range(len(y_coords)-1)]
        
        if y_diffs:
            
            # Calculate median line height
            sorted_diffs = sorted(y_diffs)
            if len(sorted_diffs) >= 5:
            
                # Use median value for better stability
                median_diff = sorted_diffs[len(sorted_diffs) // 2]
                y_similarity_threshold = max(10, min(median_diff * 0.8, 25))
            
            else:
            
                # For very few items, use a more conservative value
                min_diff = min(sorted_diffs)
                y_similarity_threshold = max(10, min_diff)
            
            logger.info(f"Calculated y_similarity_threshold: {y_similarity_threshold}")
    
    # Group boxes into rows
    rows = []
    current_row = [items_sorted_by_y[0]]
    current_row_y = items_sorted_by_y[0][3]
    
    for item in items_sorted_by_y[1:]:
        _, _, _, y = item
        
        if abs(y - current_row_y) <= y_similarity_threshold:
            
            # Add to current row if within threshold
            current_row.append(item)
        else:
           
            # Start a new row
            rows.append(current_row)
            current_row = [item]
            current_row_y = y
    
    # Add the last row
    if current_row:
        rows.append(current_row)
    
    # Sort each row by x-coordinate (left to right)
    for row in rows:
        row.sort(key=lambda item: item[2])
    
    # Create the result dictionary
    result = {}
    for row in rows:

        for key, box_info, _, _ in row:
        
            result[key] = box_info
    
    return result

def deduplicate_boxes(boxes_json): 

    """
    Deduplicates bounding boxes that have significant overlap, prioritizing by label type and confidence.
    
    Deduplication priority:
    1. For boxes with the same label: keep the one with highest confidence
    2. For boxes with different labels: prioritize 'title' over 'abandon' over 'plain_text'
    
    Args:
        boxes_json (dict): Dictionary of bounding boxes with format:
                          {'id': {'coordinates': [x, y, width, height], 'class': str, 'confidence': float}}
    
    Returns:
        dict: Deduplicated dictionary with the same format
    """
    
    def calculate_iou(box1, box2): 
    
        """Calculate the Intersection over Union (IoU) of two boxes."""
    
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate coordinates of the intersection rectangle
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        # If the boxes don't overlap, return 0
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        # Area of intersection
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Area of both boxes
        box1_area = w1 * h1
        box2_area = w2 * h2
        
        # IoU is intersection area divided by union area
        union_area = box1_area + box2_area - intersection_area
        
        return intersection_area / union_area
    
    # Define threshold for considering boxes as duplicates
    OVERLAP_THRESHOLD = 0.9
    
    # Define label priority (higher index = higher priority)
    label_priority = {'plain_text': 0, 'abandon': 1, 'title': 2}
    
    # Build a graph where nodes are box IDs and edges connect duplicate boxes
    graph = {}
    box_ids = list(boxes_json.keys())
    
    for i in range(len(box_ids)): 

        id1 = box_ids[i]
        if id1 not in graph:
            graph[id1] = []
            
        for j in range(i + 1, len(box_ids)):

            id2 = box_ids[j]
            if id2 not in graph:
                graph[id2] = []
                
            # Calculate overlap
            iou = calculate_iou(boxes_json[id1]['coordinates'], boxes_json[id2]['coordinates'])
            
            # If boxes are similar enough to be considered duplicates
            if iou > OVERLAP_THRESHOLD:
                graph[id1].append(id2)
                graph[id2].append(id1)
    
    # Find connected components (groups of duplicate boxes)
    def find_connected_component(node, visited, component): 

        visited.add(node)
        component.append(node)

        for neighbor in graph.get(node, []):
        
            if neighbor not in visited:
        
                find_connected_component(neighbor, visited, component)
        
        return component
    
    visited = set()
    duplicate_groups = []
    for node in graph:
        
        if node not in visited:
        
            component = []
            find_connected_component(node, visited, component)
        
            if len(component) > 1:  # Only consider as duplicates if more than one box
                duplicate_groups.append(component)
    
    # Create deduplicated dictionary
    deduplicated_boxes = boxes_json.copy()
    
    # Process each duplicate group
    for group in duplicate_groups:

        # Check if all boxes in the group have the same label
        labels = set(get_box_class(box_id) for box_id in group)
        
        if len(labels) == 1:

            # If all boxes have the same label, select the one with highest confidence
            box_to_keep = max(group, key = lambda id: boxes_json[id]['confidence'])

        else:

            # If boxes have different labels, apply label priority logic
            # First, find boxes with the highest priority label in this group
            max_priority = max(label_priority.get(get_box_class(box_id), -1) for box_id in group)
            highest_priority_boxes = [box_id for box_id in group if label_priority.get(get_box_class(box_id), -1) == max_priority]
            
            # Among boxes with highest priority label, select the one with highest confidence
            box_to_keep = max(highest_priority_boxes, key=lambda id: boxes_json[id]['confidence'])
        
        # Remove all other boxes in the group
        for box_id in group:
            if box_id != box_to_keep:
                deduplicated_boxes.pop(box_id, None)
    
    return deduplicated_boxes

def remove_contained_bounding_boxes(bounding_boxes): 

    """
    Process bounding boxes based on containment relationships and area coverage.
    
    A box is considered contained within another if at least 90% of its area is inside the container.
    
    For boxes that contain multiple other boxes:
    - If internal boxes occupy >50% of the container's area, remove the container box
    - If internal boxes occupy ≤50% of the container's area, remove the internal boxes
    
    Args:
        bounding_boxes (dict): Dictionary where each key is an identifier for a bounding box
                              and each value is a dictionary with 'coordinates' and 'class' keys.
                              'coordinates' is a list [x, y, width, height].
    
    Returns:
        dict: Filtered dictionary with the appropriate boxes removed.
    """

    # Find containment relationships
    containment_map = {}  # Maps box_id to list of contained box_ids
    
    # Process each bounding box to identify containment relationships
    for box_id, box_data in bounding_boxes.items():
        contained_boxes = []
        box_coords = box_data['coordinates']
        
        # Extract coordinates
        x1, y1, width1, height1 = box_coords
        right1 = x1 + width1
        bottom1 = y1 + height1
        
        # Check all other bounding boxes
        for other_id, other_data in bounding_boxes.items():
            # Skip comparing with itself
            if other_id == box_id:
                continue
                
            other_coords = other_data['coordinates']
            x2, y2, width2, height2 = other_coords
            right2 = x2 + width2
            bottom2 = y2 + height2
            
            # Calculate intersection coordinates
            intersection_x1 = max(x1, x2)
            intersection_y1 = max(y1, y2)
            intersection_x2 = min(right1, right2)
            intersection_y2 = min(bottom1, bottom2)
            
            # Check if there is an intersection
            if intersection_x1 < intersection_x2 and intersection_y1 < intersection_y2:
                # Calculate intersection area
                intersection_width = intersection_x2 - intersection_x1
                intersection_height = intersection_y2 - intersection_y1
                intersection_area = intersection_width * intersection_height
                
                # Calculate the area of the potentially contained box
                other_box_area = width2 * height2
                
                # Check if at least 90% of the other box is inside this box
                if intersection_area >= 0.9 * other_box_area:
                    contained_boxes.append(other_id)
        
        # Only store boxes that contain multiple other boxes
        if len(contained_boxes) > 0:
            containment_map[box_id] = contained_boxes
    
    # Set of IDs to remove
    boxes_to_remove = set()
    
    # Process each container with multiple contained boxes
    for container_id, contained_ids in containment_map.items():
        # Calculate container area
        x, y, width, height = bounding_boxes[container_id]['coordinates']
        container_area = width * height
        
        # Calculate total area of contained boxes
        total_contained_area = 0
        for contained_id in contained_ids:
            cx, cy, cwidth, cheight = bounding_boxes[contained_id]['coordinates']
            contained_area = cwidth * cheight
            total_contained_area += contained_area
        
        # Decision based on area comparison
        if total_contained_area > (container_area / 2):
            # Internal boxes take up more than half the area, remove container
            boxes_to_remove.add(container_id)
        else:
            # Internal boxes take up less than half the area, remove contained boxes
            boxes_to_remove.update(contained_ids)
    
    # Create filtered result by removing the appropriate boxes
    filtered_bounding_boxes = {k: v for k, v in bounding_boxes.items() if k not in boxes_to_remove}
    
    return filtered_bounding_boxes