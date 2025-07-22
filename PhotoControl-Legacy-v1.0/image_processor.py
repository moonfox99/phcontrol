#!/usr/bin/env python3
"""
Azimuth Grid Image Processor
Basic foundation for processing images with azimuth grids
"""

import math
from PIL import Image, ImageDraw, ImageOps
import os

class AzimuthImageProcessor:
    def __init__(self, image_path, center_x=None, center_y=None, scale=300):
        """
        Initialize the processor with an image
        
        Args:
            image_path: Path to the image file
            center_x, center_y: Center coordinates of azimuth grid (if None, use image center)
            scale: Scale value for range calculations (default 300)
        """
        self.image_path = image_path
        self.original_image = Image.open(image_path)  # Keep original unchanged
        self.image = self.original_image.copy()  # Working copy
        self.scale = scale
        
        # Image adjustments
        self.rotation_angle = 0
        self.offset_x = 0
        self.offset_y = 0
        
        # Set center coordinates (default to image center if not specified)
        self.center_x = center_x if center_x is not None else self.image.width // 2
        self.center_y = center_y if center_y is not None else self.image.height // 2
        
        print(f"Image loaded: {image_path}")
        print(f"Image size: {self.image.width} x {self.image.height}")
        print(f"Grid center: ({self.center_x}, {self.center_y})")
        print(f"Scale: {self.scale}")
    
    def rotate_image(self, angle):
        """
        Rotate the image by specified angle (degrees)
        Positive angle = clockwise rotation
        
        Args:
            angle: Rotation angle in degrees
        """
        self.rotation_angle += angle
        self.rotation_angle = self.rotation_angle % 360  # Keep between 0-360
        
        # Rotate image (PIL rotates counter-clockwise, so we negate)
        self.image = self.original_image.rotate(-self.rotation_angle, expand=True, fillcolor='white')
        
        # Update center coordinates after rotation
        self.center_x = self.image.width // 2 + self.offset_x
        self.center_y = self.image.height // 2 + self.offset_y
        
        print(f"Image rotated by {angle}° (total: {self.rotation_angle}°)")
        print(f"New size: {self.image.width} x {self.image.height}")
        print(f"New center: ({self.center_x}, {self.center_y})")
    
    def move_center(self, dx, dy):
        """
        Move the azimuth grid center point
        
        Args:
            dx: Horizontal offset (positive = right)
            dy: Vertical offset (positive = down)
        """
        self.offset_x += dx
        self.offset_y += dy
        
        # Update center coordinates
        self.center_x = self.image.width // 2 + self.offset_x
        self.center_y = self.image.height // 2 + self.offset_y
        
        # Ensure center stays within image bounds
        self.center_x = max(0, min(self.center_x, self.image.width - 1))
        self.center_y = max(0, min(self.center_y, self.image.height - 1))
        
        print(f"Center moved by ({dx}, {dy})")
        print(f"New center: ({self.center_x}, {self.center_y})")
    
    def reset_adjustments(self):
        """
        Reset all adjustments to original image
        """
        self.image = self.original_image.copy()
        self.rotation_angle = 0
        self.offset_x = 0
        self.offset_y = 0
        self.center_x = self.image.width // 2
        self.center_y = self.image.height // 2
        
        print("Image reset to original state")
        print(f"Center: ({self.center_x}, {self.center_y})")
    
    def auto_rotate_exif(self):
        """
        Auto-rotate image based on EXIF orientation data
        This handles photos taken with rotated cameras
        """
        try:
            # Use PIL's built-in EXIF orientation correction
            corrected_image = ImageOps.exif_transpose(self.original_image)
            if corrected_image != self.original_image:
                self.original_image = corrected_image
                self.image = corrected_image.copy()
                self.center_x = self.image.width // 2
                self.center_y = self.image.height // 2
                print("Image auto-rotated based on EXIF data")
            else:
                print("No EXIF rotation needed")
        except Exception as e:
            print(f"Could not read EXIF data: {e}")
    
    def get_center_preview(self):
        """
        Create a preview image showing the current center point
        Useful for adjusting center position
        
        Returns:
            PIL Image: Image with center marked
        """
        preview = self.image.copy()
        draw = ImageDraw.Draw(preview)
        
        # Draw crosshairs at center
        cross_size = 20
        line_width = 2
        
        # Horizontal line
        draw.line([
            (self.center_x - cross_size, self.center_y),
            (self.center_x + cross_size, self.center_y)
        ], fill='red', width=line_width)
        
        # Vertical line
        draw.line([
            (self.center_x, self.center_y - cross_size),
            (self.center_x, self.center_y + cross_size)
        ], fill='red', width=line_width)
        
        # Draw center circle
        circle_radius = 3
        draw.ellipse([
            self.center_x - circle_radius, self.center_y - circle_radius,
            self.center_x + circle_radius, self.center_y + circle_radius
        ], fill='red', outline='white', width=1)
        
        return preview
    
    def pixel_to_azimuth_range(self, click_x, click_y):
        """
        Convert pixel coordinates to azimuth and range
        
        Scale is based on the distance from center straight down to bottom edge (azimuth 180°)
        
        Args:
            click_x, click_y: Pixel coordinates of clicked point
            
        Returns:
            tuple: (azimuth_degrees, range_units)
        """
        # Calculate relative coordinates from center
        dx = click_x - self.center_x
        dy = self.center_y - click_y  # Invert Y axis (image coordinates vs mathematical coordinates)
        
        # Calculate range (distance from center)
        range_pixels = math.sqrt(dx**2 + dy**2)
        
        # Calculate distance from center to bottom edge (azimuth 180°)
        # This is our reference distance for the scale
        reference_pixel_distance = self.image.height - self.center_y
        
        # Convert pixel distance to actual range based on scale
        # Scale represents the range at the bottom edge of the image
        range_actual = (range_pixels / reference_pixel_distance) * self.scale
        
        # Calculate azimuth (angle from north, clockwise)
        azimuth_radians = math.atan2(dx, dy)  # atan2(x, y) for standard azimuth (0° = North)
        azimuth_degrees = math.degrees(azimuth_radians)
        
        # Normalize azimuth to 0-360 degrees
        if azimuth_degrees < 0:
            azimuth_degrees += 360
            
        return azimuth_degrees, range_actual
    
    def draw_line_to_point(self, click_x, click_y, end_x, end_y, line_color="red", line_width=2):
        """
        Draw a line from clicked point to a fixed reference point
        
        Args:
            click_x, click_y: Starting point coordinates
            end_x, end_y: End point coordinates
            line_color: Color of the line
            line_width: Width of the line
            
        Returns:
            PIL Image: Image with drawn line
        """
        # Create a copy of the image to draw on
        img_with_line = self.image.copy()
        draw = ImageDraw.Draw(img_with_line)
        
        # Draw the line
        draw.line([(click_x, click_y), (end_x, end_y)], fill=line_color, width=line_width)
        
        # Optionally draw a small circle at the clicked point
        circle_radius = 3
        draw.ellipse([
            click_x - circle_radius, click_y - circle_radius,
            click_x + circle_radius, click_y + circle_radius
        ], fill=line_color)
        
        return img_with_line
    
    def process_click(self, click_x, click_y, reference_x=None, reference_y=None):
        """
        Process a click event: calculate coordinates and draw line
        
        Args:
            click_x, click_y: Clicked coordinates
            reference_x, reference_y: Reference point for line (default: right edge middle)
            
        Returns:
            tuple: (azimuth, range, processed_image)
        """
        # Calculate azimuth and range
        azimuth, range_val = self.pixel_to_azimuth_range(click_x, click_y)
        
        # Set default reference point if not provided
        if reference_x is None:
            reference_x = self.image.width - 50  # 50 pixels from right edge
        if reference_y is None:
            reference_y = click_y  # Same height as clicked point
        
        # Draw line to reference point
        processed_image = self.draw_line_to_point(click_x, click_y, reference_x, reference_y)
        
        return azimuth, range_val, processed_image

# Test function with adjustment features
def test_processor_with_adjustments():
    """
    Enhanced test function to demonstrate image adjustments
    """
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Please add a test image named '{test_image_path}' to your project folder")
        return
    
    # Initialize processor
    processor = AzimuthImageProcessor(test_image_path, scale=300)
    
    # Auto-correct EXIF rotation first
    processor.auto_rotate_exif()
    
    # Save center preview
    center_preview = processor.get_center_preview()
    center_preview.save("center_preview_original.jpg")
    print("Center preview saved as: center_preview_original.jpg")
    
    # Demonstrate adjustments
    print("\n=== Testing Image Adjustments ===")
    
    # Test rotation
    print("\n1. Rotating image 45 degrees clockwise...")
    processor.rotate_image(45)
    rotated_preview = processor.get_center_preview()
    rotated_preview.save("center_preview_rotated.jpg")
    
    # Test center movement
    print("\n2. Moving center 50 pixels right, 30 pixels down...")
    processor.move_center(50, 30)
    moved_preview = processor.get_center_preview()
    moved_preview.save("center_preview_moved.jpg")
    
    # Test a click with adjustments
    print("\n3. Testing click with adjustments...")
    test_x, test_y = processor.center_x + 100, processor.center_y - 50
    azimuth, range_val, processed_img = processor.process_click(test_x, test_y)
    processed_img.save("output_with_adjustments.jpg")
    print(f"Click at ({test_x}, {test_y})")
    print(f"Azimuth: {azimuth:.1f}°, Range: {range_val:.1f} units")
    
    # Reset and test
    print("\n4. Resetting to original...")
    processor.reset_adjustments()
    reset_preview = processor.get_center_preview()
    reset_preview.save("center_preview_reset.jpg")
    
    print("\n=== Manual Adjustment Guide ===")
    print("Available methods:")
    print("- processor.rotate_image(angle)  # Positive = clockwise")
    print("- processor.move_center(dx, dy)  # dx=right, dy=down")
    print("- processor.reset_adjustments()  # Back to original")
    print("- processor.auto_rotate_exif()   # Auto-correct camera rotation")
    print("- processor.get_center_preview() # See current center position")

def interactive_adjustment_demo():
    """
    Interactive demo for manual adjustments
    """
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Please add a test image named '{test_image_path}' to your project folder")
        return
    
    processor = AzimuthImageProcessor(test_image_path, scale=300)
    processor.auto_rotate_exif()
    
    print("=== Interactive Adjustment Demo ===")
    print("Commands:")
    print("  r45    - rotate 45° clockwise")
    print("  r-90   - rotate 90° counter-clockwise")
    print("  m10,20 - move center right 10, down 20")
    print("  m-10,-20 - move center left 10, up 20")
    print("  reset  - reset to original")
    print("  preview - save center preview")
    print("  test   - test click at center+100,center-50")
    print("  quit   - exit")
    
    while True:
        # Save current preview
        preview = processor.get_center_preview()
        preview.save("current_preview.jpg")
        
        cmd = input("\nEnter command (or 'quit'): ").strip().lower()
        
        if cmd == 'quit':
            break
        elif cmd == 'reset':
            processor.reset_adjustments()
        elif cmd == 'preview':
            preview.save(f"manual_preview_{processor.rotation_angle}deg.jpg")
            print(f"Preview saved")
        elif cmd == 'test':
            x, y = processor.center_x + 100, processor.center_y - 50
            azimuth, range_val, result = processor.process_click(x, y)
            result.save("manual_test_result.jpg")
            print(f"Test click: Azimuth {azimuth:.1f}°, Range {range_val:.1f}")
        elif cmd.startswith('r'):
            try:
                angle = float(cmd[1:])
                processor.rotate_image(angle)
            except ValueError:
                print("Invalid rotation format. Use: r45 or r-90")
        elif cmd.startswith('m'):
            try:
                coords = cmd[1:].split(',')
                dx, dy = float(coords[0]), float(coords[1])
                processor.move_center(dx, dy)
            except (ValueError, IndexError):
                print("Invalid move format. Use: m10,20 or m-10,-20")
        else:
            print("Unknown command")

# Test function with new range calculation
def test_range_calculation():
    """
    Test function to demonstrate the new range calculation method
    """
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Please add a test image named '{test_image_path}' to your project folder")
        return
    
    # Test with different scales
    scales = [25, 35, 50, 75, 80, 90, 100, 150, 200, 250, 300, 350]
    
    for scale in scales:
        print(f"\n=== Testing with Scale {scale} ===")
        processor = AzimuthImageProcessor(test_image_path, scale=scale)
        processor.auto_rotate_exif()
        
        # Calculate distances to edges
        distances_to_edges = [
            processor.center_x,  # Left
            processor.image.width - processor.center_x,  # Right
            processor.center_y,  # Top
            processor.image.height - processor.center_y  # Bottom
        ]
        max_pixel_distance = max(distances_to_edges)
        
        print(f"Image size: {processor.image.width}x{processor.image.height}")
        print(f"Center: ({processor.center_x}, {processor.center_y})")
        print(f"Max distance to edge: {max_pixel_distance} pixels")
        print(f"Scale: {scale} units at max distance")
        print(f"Units per pixel: {scale/max_pixel_distance:.3f}")
        
        # Test some points
        test_points = [
            (processor.center_x, processor.center_y),  # Center
            (processor.center_x + max_pixel_distance//2, processor.center_y),  # Half distance east
            (processor.center_x, processor.center_y + max_pixel_distance//2),  # Half distance south
            (processor.center_x + max_pixel_distance, processor.center_y),  # Max distance east (if possible)
        ]
        
        for i, (x, y) in enumerate(test_points):
            # Ensure point is within image bounds
            x = max(0, min(x, processor.image.width - 1))
            y = max(0, min(y, processor.image.height - 1))
            
            azimuth, range_val = processor.pixel_to_azimuth_range(x, y)
            pixel_distance = ((x - processor.center_x)**2 + (y - processor.center_y)**2)**0.5
            
            print(f"  Point {i+1}: ({x}, {y}) -> {azimuth:.1f}°, {range_val:.1f} units ({pixel_distance:.1f} px)")

def interactive_scale_demo():
    """
    Interactive demo for testing different scales on the same point
    """
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"Please add a test image named '{test_image_path}' to your project folder")
        return
    
    processor = AzimuthImageProcessor(test_image_path, scale=300)
    processor.auto_rotate_exif()
    
    print("=== Scale Comparison Demo ===")
    print(f"Image: {processor.image.width}x{processor.image.height}")
    print(f"Center: ({processor.center_x}, {processor.center_y})")
    
    # Pick a test point
    test_x = processor.center_x + 100
    test_y = processor.center_y + 50
    
    print(f"\nTesting point: ({test_x}, {test_y})")
    print("Scale -> Range calculation:")
    
    for scale in [25, 35, 50, 75, 80, 90, 100, 150, 200, 250, 300, 350]:
        processor.scale = scale
        azimuth, range_val = processor.pixel_to_azimuth_range(test_x, test_y)
        print(f"  Scale {scale:3d} -> Range {range_val:6.1f} units (Azimuth: {azimuth:.1f}°)")
    
    print(f"\nAs you can see, azimuth stays the same ({azimuth:.1f}°) but range changes with scale!")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Automatic adjustment test")
    print("2. Interactive adjustment demo")
    print("3. Range calculation test")
    print("4. Scale comparison demo")
    
    choice = input("Enter 1, 2, 3, or 4: ").strip()
    
    if choice == "1":
        test_processor_with_adjustments()
    elif choice == "2":
        interactive_adjustment_demo()
    elif choice == "3":
        test_range_calculation()
    elif choice == "4":
        interactive_scale_demo()
    else:
        test_processor_with_adjustments()