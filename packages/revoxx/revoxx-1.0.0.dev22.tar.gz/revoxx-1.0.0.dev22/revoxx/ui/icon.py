"""Application icon creation for Revoxx."""

import tkinter as tk
from typing import Optional, List, Tuple
from pathlib import Path


class AppIcon:
    """Creates and manages the application icon.

    This class loads a PNG icon for use as the window icon.
    """

    @staticmethod
    def create_icon(icon_path: Path) -> Optional[tk.PhotoImage]:
        """Create icon from PNG file.

        Args:
            icon_path: Path to the PNG icon file

        Returns:
            PhotoImage object or None if creation fails
        """
        try:
            if not icon_path.exists():
                print(f"Icon file not found: {icon_path}")
                return None

            # Simply load and return the PNG at original size
            # macOS can handle large icons and will scale them as needed
            img = tk.PhotoImage(file=str(icon_path))

            if icon_path.parent.name == "debug":
                print(f"Loaded icon: {img.width()}x{img.height()} pixels")

            return img

        except Exception as e:
            print(f"Error creating icon from PNG: {e}")
            return None

    @staticmethod
    def create_scaled_icons(icon_path: Path, sizes: List[int] = [16, 32, 64, 128]) -> List[tk.PhotoImage]:
        """Create multiple scaled versions of an icon.

        Args:
            icon_path: Path to the PNG icon file
            sizes: List of sizes to create (in pixels)

        Returns:
            List of PhotoImage objects at different sizes
        """
        icons = []
        
        try:
            if not icon_path.exists():
                return icons
                
            # Load the original image
            original = tk.PhotoImage(file=str(icon_path))
            original_width = original.width()
            original_height = original.height()
            
            for size in sizes:
                # Calculate scaling factor
                scale = size / max(original_width, original_height)
                
                if scale >= 1:
                    # Don't upscale, just use original
                    icons.append(original)
                else:
                    # Downscale using subsample
                    # subsample works with integer factors, so we need to find the closest
                    factor = int(1 / scale)
                    if factor > 0:
                        scaled = original.subsample(factor, factor)
                        icons.append(scaled)
            
            return icons
            
        except Exception:
            # Return whatever we managed to create
            return icons
