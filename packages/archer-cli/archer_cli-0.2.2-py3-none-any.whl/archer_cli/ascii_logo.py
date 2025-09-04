#!/usr/bin/env python3
"""
ASCII art generator for Archer logo using colored blocks.
Converts PNG images to colored ASCII art using Unicode half-blocks and full blocks.
"""

import os
from PIL import Image
import numpy as np
from rich.console import Console
from rich.text import Text
from rich import box
from rich.panel import Panel
from typing import Tuple, List

# Unicode block characters
FULL_BLOCK = "█"
UPPER_HALF_BLOCK = "▀"
LOWER_HALF_BLOCK = "▄"
LIGHT_SHADE = "░"
MEDIUM_SHADE = "▒"
DARK_SHADE = "▓"

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string."""
    return f"#{r:02x}{g:02x}{b:02x}"

def blend_rgba_with_background(r: int, g: int, b: int, a: int, bg_rgb: tuple = (0x1e, 0x1e, 0x1e)) -> tuple:
    """Blend RGBA pixel with background color."""
    if a == 255:
        return (r, g, b)
    
    alpha = a / 255.0
    bg_r, bg_g, bg_b = bg_rgb
    
    return (
        int(r * alpha + bg_r * (1 - alpha)),
        int(g * alpha + bg_g * (1 - alpha)),
        int(b * alpha + bg_b * (1 - alpha))
    )

def get_dominant_color(pixels: np.ndarray) -> str:
    """Get dominant color from a group of pixels."""
    if pixels.size == 0:
        return "#000000"
    
    # If we have alpha channel, consider transparency
    if pixels.shape[-1] == 4:
        # Check if most pixels are transparent
        alpha_values = pixels[:, :, 3]
        if np.mean(alpha_values) < 128:
            return "#000000"
        
        # Use only non-transparent pixels for color calculation
        opaque_mask = alpha_values >= 128
        if not np.any(opaque_mask):
            return "#000000"
        
        opaque_pixels = pixels[opaque_mask]
        avg_color = np.mean(opaque_pixels, axis=0)
    else:
        avg_color = np.mean(pixels.reshape(-1, pixels.shape[-1]), axis=0)
    
    if len(avg_color) >= 3:
        r, g, b = avg_color[:3]
        a = avg_color[3] if len(avg_color) > 3 else 255
        blended_rgb = blend_rgba_with_background(int(r), int(g), int(b), int(a))
        return rgb_to_hex(*blended_rgb)
    
    return "#000000"

def resize_image_for_ascii(image: Image.Image, max_width: int = 35, max_height: int = 18) -> Image.Image:
    """Resize image while maintaining aspect ratio for ASCII conversion."""
    original_width, original_height = image.size
    
    # Calculate aspect ratio
    aspect_ratio = original_width / original_height
    
    # Adjust for terminal character aspect ratio (characters are taller than wide)
    terminal_aspect_correction = 2.0
    adjusted_aspect = aspect_ratio * terminal_aspect_correction
    
    # Calculate new dimensions
    if adjusted_aspect > max_width / max_height:
        # Width is the limiting factor
        new_width = max_width
        new_height = int(max_width / adjusted_aspect)
    else:
        # Height is the limiting factor  
        new_height = max_height
        new_width = int(max_height * adjusted_aspect)
    
    # Ensure we don't exceed limits
    new_width = min(new_width, max_width)
    new_height = min(new_height, max_height)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def image_to_ascii_blocks(image_path: str, width: int = 40, height: int = 20) -> List[Text]:
    """Convert image to colored ASCII art using blocks - vtree inspired implementation."""
    try:
        # Open and process image
        image = Image.open(image_path)
        
        # Convert to RGBA to handle transparency
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Resize for ASCII art
        image = resize_image_for_ascii(image, width, height)
        
        # Convert to numpy array for easier processing
        pixels = np.array(image)
        img_height, img_width = pixels.shape[:2]
        
        ascii_lines = []
        
        # Process image in pairs of rows for half-blocks
        for y in range(0, img_height, 2):
            line = Text()
            
            for x in range(img_width):
                # Get upper pixel
                upper_pixel = pixels[y, x] if y < img_height else [0, 0, 0, 0]
                
                # Get lower pixel (if exists)
                lower_pixel = pixels[y + 1, x] if (y + 1) < img_height else [0, 0, 0, 0]
                
                # Blend pixels with background and get hex colors
                upper_r, upper_g, upper_b, upper_a = upper_pixel
                lower_r, lower_g, lower_b, lower_a = lower_pixel
                
                upper_blended = blend_rgba_with_background(upper_r, upper_g, upper_b, upper_a)
                lower_blended = blend_rgba_with_background(lower_r, lower_g, lower_b, lower_a)
                
                upper_hex = rgb_to_hex(*upper_blended)
                lower_hex = rgb_to_hex(*lower_blended)
                
                # Check if pixels are essentially transparent/black
                upper_is_bg = upper_a < 128 or (int(upper_r) + int(upper_g) + int(upper_b) < 30)
                lower_is_bg = lower_a < 128 or (int(lower_r) + int(lower_g) + int(lower_b) < 30)
                
                # Choose block character and colors
                if upper_is_bg and lower_is_bg:
                    # Both transparent/black - use space
                    line.append(" ")
                elif not upper_is_bg and lower_is_bg:
                    # Only upper has color - use upper half block
                    line.append(UPPER_HALF_BLOCK, style=upper_hex)
                elif upper_is_bg and not lower_is_bg:
                    # Only lower has color - use lower half block  
                    line.append(LOWER_HALF_BLOCK, style=lower_hex)
                elif upper_hex == lower_hex:
                    # Same color - use full block
                    line.append(FULL_BLOCK, style=upper_hex)
                else:
                    # Different colors - use half block with proper fg/bg
                    line.append(UPPER_HALF_BLOCK, style=f"{upper_hex} on {lower_hex}")
            
            ascii_lines.append(line)
        
        return ascii_lines
        
    except Exception as e:
        # Return error message as Text
        error_text = Text(f"Error loading logo: {e}", style="red")
        return [error_text]

def generate_archer_logo_ascii(console_width: int = 80) -> List[Text]:
    """Generate the Archer ASCII logo."""
    
    logo_path = "/Users/marcokotrotsos/projects/archer-code/logo.png"
    
    # Check if logo exists
    if not os.path.exists(logo_path):
        return [Text("Archer logo not found", style="yellow")]
    
    # Determine size based on console width (slightly narrower)
    logo_width = min(40, max(16, console_width // 3))
    logo_height = min(20, max(8, logo_width // 2))
    
    ascii_lines = image_to_ascii_blocks(logo_path, logo_width, logo_height)
    
    return ascii_lines

def display_startup_logo(console: Console = None) -> None:
    """Display the Archer startup logo with ASCII art."""
    if console is None:
        console = Console()
    
    # Generate ASCII logo
    ascii_lines = generate_archer_logo_ascii(console.width)
    
    # Display logo directly without panels
    console.print()  # Add top spacing
    
    # Print each line of ASCII art directly
    for line in ascii_lines:
        console.print(line, justify="center")
    
    console.print()  # Add spacing after logo
    
    # Create title
    title_text = Text()
    title_text.append("ARCHER", style="bold cyan")
    title_text.append(" AI CODING ASSISTANT", style="bright_white")
    
    # Print title centered
    console.print(title_text, justify="center")

# Test function
def test_logo_generation():
    """Test the logo generation."""
    console = Console()
    
    print("Testing Archer ASCII Logo Generation")
    print("=" * 50)
    
    display_startup_logo(console)
    
    print("\n" + "=" * 50)
    print("Logo test complete!")

if __name__ == "__main__":
    test_logo_generation()