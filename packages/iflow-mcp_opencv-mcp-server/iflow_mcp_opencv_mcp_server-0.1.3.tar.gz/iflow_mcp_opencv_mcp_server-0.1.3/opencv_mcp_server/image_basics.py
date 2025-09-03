"""
OpenCV MCP Server - Image Basics

This module provides basic image handling and manipulation tools using OpenCV.
It includes functionality for reading, saving, and manipulating images.
"""

import cv2
import numpy as np
import os
import logging
import datetime
import subprocess
import platform
from typing import Optional, Dict, Any, List, Union
# Import utility functions from utils
from .utils import get_image_info, save_and_display, get_timestamp

logger = logging.getLogger("opencv-mcp-server.image_basics")

# Tool implementations
def save_image_tool(path_in: str, path_out: str) -> Dict[str, Any]:
    """
    Save an image to a file
    
    Args:
        path_in: Path to input image
        path_out: Output file path
        
    Returns:
        Dict: Status information
    """
    # Read input image
    img = cv2.imread(path_in)
    if img is None:
        raise ValueError(f"Failed to read image from path: {path_in}")
    
    # Ensure directory exists
    directory = os.path.dirname(path_out)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save and display
    new_path = save_and_display(img, path_out, "save")
    
    return {
        "success": True,
        "path": new_path,
        "size_bytes": os.path.getsize(new_path),
        "size_mb": round(os.path.getsize(new_path) / (1024 * 1024), 2),
        "output_path": new_path  # Return path for chaining operations
    }

def convert_color_space_tool(image_path: str, source_space: str, target_space: str) -> Dict[str, Any]:
    """
    Convert image between color spaces
    
    Args:
        image_path: Path to the image file
        source_space: Source color space (BGR, RGB, GRAY, HSV, etc.)
        target_space: Target color space (BGR, RGB, GRAY, HSV, etc.)
        
    Returns:
        Dict: Converted image information and path
    """
    # Read image from path
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image from path: {image_path}")
    
    # Build comprehensive color space conversion map
    def build_color_conversion_map():
        """Build a comprehensive mapping of color space conversions"""
        conversions = {}

        # Get all COLOR_ constants from cv2
        color_constants = [attr for attr in dir(cv2) if attr.startswith('COLOR_')]

        for constant in color_constants:
            # More robust parsing - handle different naming patterns
            constant_suffix = constant[6:]  # Remove COLOR_ prefix
            if '2' in constant_suffix:
                # Split on '2' and take only first split to handle edge cases
                parts = constant_suffix.split('2', 1)  # Split only on first '2'
                if len(parts) == 2 and parts[0] and parts[1]:  # Ensure both parts are non-empty
                    source = parts[0]
                    target = parts[1]
                    key = f"{source}2{target}"
                    conversions[key] = getattr(cv2, constant)

        # Debug: Log the number of conversions found
        logger.debug(f"Built color conversion map with {len(conversions)} conversions")

        return conversions

    # Get all available conversions
    color_conversions = build_color_conversion_map()

    # Normalize input color space names to match OpenCV constants
    def normalize_color_space(space_name):
        """Normalize color space name to match OpenCV constants"""
        # Handle common aliases
        aliases = {
            'GRAY': 'GRAY',
            'GREY': 'GRAY',
            'HSL': 'HLS',  # OpenCV uses HLS instead of HSL
            'LAB': 'Lab',
            'LUV': 'Luv',
            'YCRCB': 'YCrCb',
            'YCR_CB': 'YCrCb',
        }

        upper_name = space_name.upper()
        return aliases.get(upper_name, space_name.upper())

    # Normalize color space names
    norm_source = normalize_color_space(source_space)
    norm_target = normalize_color_space(target_space)

    # Try direct conversion first
    direct_key = f"{norm_source}2{norm_target}"

    if direct_key in color_conversions:
        conversion_code = color_conversions[direct_key]
        converted = cv2.cvtColor(img, conversion_code)
    else:
        # Try two-step conversion via BGR
        source_to_bgr_key = f"{norm_source}2BGR"
        bgr_to_target_key = f"BGR2{norm_target}"

        if source_to_bgr_key in color_conversions and bgr_to_target_key in color_conversions:
            # First convert to BGR
            temp_img = cv2.cvtColor(img, color_conversions[source_to_bgr_key])
            # Then convert from BGR to target
            converted = cv2.cvtColor(temp_img, color_conversions[bgr_to_target_key])
        else:
            # List available conversions for debugging
            available_from_source = [k for k in color_conversions.keys() if k.startswith(f"{norm_source}2")]
            available_to_target = [k for k in color_conversions.keys() if k.endswith(f"2{norm_target}")]

            raise ValueError(
                f"Unsupported color space conversion: {source_space} to {target_space}. "
                f"Available conversions from {norm_source}: {available_from_source}. "
                f"Available conversions to {norm_target}: {available_to_target}"
            )

    # For display purposes, ensure we have a BGR image
    display_img = converted

    # If target is not BGR and not grayscale, try to convert to BGR for display
    if norm_target not in ['BGR', 'GRAY'] and len(converted.shape) > 2:
        display_key = f"{norm_target}2BGR"
        if display_key in color_conversions:
            try:
                display_img = cv2.cvtColor(converted, color_conversions[display_key])
            except:
                # If conversion fails, use original converted image
                display_img = converted

    # Save and display
    new_path = save_and_display(display_img, image_path, f"convert_{source_space}_to_{target_space}")
    
    return {
        "source_space": source_space,
        "target_space": target_space,
        "normalized_source": norm_source,
        "normalized_target": norm_target,
        "conversion_used": direct_key if direct_key in color_conversions else f"{source_to_bgr_key} -> {bgr_to_target_key}",
        "info": get_image_info(converted),
        "path": new_path,
        "output_path": new_path  # Return path for chaining operations
    }

def resize_image_tool(image_path: str, width: int, height: int, interpolation: str = "INTER_LINEAR") -> Dict[str, Any]:
    """
    Resize an image to specific dimensions
    
    Args:
        image_path: Path to the image file
        width: Target width in pixels
        height: Target height in pixels
        interpolation: Interpolation method
        
    Returns:
        Dict: Resized image information and path
    """
    # Read image from path
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image from path: {image_path}")
    
    # Map interpolation methods to OpenCV constants
    interp_methods = {
        "INTER_NEAREST": cv2.INTER_NEAREST,
        "INTER_LINEAR": cv2.INTER_LINEAR,
        "INTER_CUBIC": cv2.INTER_CUBIC,
        "INTER_AREA": cv2.INTER_AREA,
        "INTER_LANCZOS4": cv2.INTER_LANCZOS4
    }
    
    interp = interp_methods.get(interpolation, cv2.INTER_LINEAR)
    
    # Perform the resize
    resized = cv2.resize(img, (width, height), interpolation=interp)
    
    # Save and display
    new_path = save_and_display(resized, image_path, f"resize_{width}x{height}")
    
    return {
        "width": width,
        "height": height,
        "interpolation": interpolation,
        "info": get_image_info(resized),
        "original_info": get_image_info(img),
        "path": new_path,
        "output_path": new_path  # Return path for chaining operations
    }

def crop_image_tool(image_path: str, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """
    Crop a region from an image
    
    Args:
        image_path: Path to the image file
        x: X-coordinate of top-left corner
        y: Y-coordinate of top-left corner
        width: Width of crop region
        height: Height of crop region
        
    Returns:
        Dict: Cropped image information and path
    """
    # Read image from path
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image from path: {image_path}")
    
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Validate crop parameters
    if x < 0 or y < 0 or (x + width) > img_width or (y + height) > img_height:
        raise ValueError(f"Crop region ({x}, {y}, {width}, {height}) is outside image bounds ({img_width}, {img_height})")
    
    # Perform the crop
    cropped = img[y:y+height, x:x+width]
    
    # Save and display
    new_path = save_and_display(cropped, image_path, f"crop_{x}_{y}_{width}_{height}")
    
    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "info": get_image_info(cropped),
        "original_info": get_image_info(img),
        "path": new_path,
        "output_path": new_path  # Return path for chaining operations
    }

def get_image_stats_tool(image_path: str, channels: bool = True) -> Dict[str, Any]:
    """
    Get statistical information about an image
    
    Args:
        image_path: Path to the image file
        channels: Whether to calculate stats per channel
        
    Returns:
        Dict: Image statistics and paths
    """
    # Read image from path
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image from path: {image_path}")
    
    # Calculate basic statistics
    info = get_image_info(img)
    
    # Calculate mean and standard deviation
    mean, stddev = cv2.meanStdDev(img)
    
    stats = {
        "info": info,
        "min": float(np.min(img)),
        "max": float(np.max(img)),
        "mean": float(np.mean(img)),
        "stddev": float(np.std(img))
    }
    
    # Calculate per-channel statistics if requested
    if channels and len(img.shape) > 2:
        channel_stats = []
        for i in range(img.shape[2]):
            channel = img[:,:,i]
            channel_stats.append({
                "channel": i,
                "min": float(np.min(channel)),
                "max": float(np.max(channel)),
                "mean": float(np.mean(channel)),
                "stddev": float(np.std(channel))
            })
        stats["channels"] = channel_stats
    
    # Calculate histogram data
    hist_data = []
    if len(img.shape) > 2:  # Color image
        for i in range(img.shape[2]):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            hist_data.append(hist.flatten().tolist())
    else:  # Grayscale image
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_data.append(hist.flatten().tolist())
    
    stats["histogram"] = hist_data
    
    # Create a visual histogram
    hist_img = np.zeros((400, 512, 3), np.uint8)
    hist_img[:] = (255, 255, 255)  # White background
    
    colors = [(255,0,0), (0,255,0), (0,0,255)]  # BGR for each channel
    
    for i, hist_channel in enumerate(hist_data):
        if i >= 3:  # Only handle up to 3 channels
            break
            
        # Normalize histogram for display
        hist_max = max(hist_channel)
        if hist_max > 0:
            normalized = [h * 380 / hist_max for h in hist_channel]
            
            # Draw histogram lines
            for x in range(256):
                pt1 = (2*x, 399)
                pt2 = (2*x, 399 - int(normalized[x]))
                cv2.line(hist_img, pt1, pt2, colors[i], 1)
    
    # Save and display histogram
    hist_path = save_and_display(hist_img, image_path, "histogram")
    
    # Display the original image as well
    display_path = save_and_display(img, image_path, "stats")
    
    stats["histogram_image_path"] = hist_path
    stats["image_path"] = display_path
    stats["output_path"] = display_path  # Return path for chaining operations
    
    return stats

def register_tools(mcp):
    """
    Register all image basics tools with the MCP server
    
    Args:
        mcp: The MCP server instance
    """
    # Register optimized tool implementations
    mcp.add_tool(save_image_tool)
    mcp.add_tool(convert_color_space_tool)
    mcp.add_tool(resize_image_tool)
    mcp.add_tool(crop_image_tool)
    mcp.add_tool(get_image_stats_tool)
