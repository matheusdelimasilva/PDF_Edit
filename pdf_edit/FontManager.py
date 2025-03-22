import os
import sys
import requests
import zipfile
import io
from pathlib import Path
from typing import Optional, List, Dict

class FontManager:
    """Manages font discovery and downloading for the PDF Editor."""
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.font_extensions = [".ttf", ".otf", ".woff", ".woff2"]

    def set_verbose(self, verbose):
        """Set verbose mode for detailed output."""
        self.verbose = verbose
    
    def get_system_font_dirs(self) -> List[str]:
        """Get the system's font directories based on the operating system."""
        if sys.platform == "win32":
            return [
                os.path.join(os.environ["WINDIR"], "Fonts"),
                os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts"),
            ]
        elif sys.platform == "darwin":
            return [
                "/Library/Fonts",
                "/System/Library/Fonts",
                os.path.expanduser("~/Library/Fonts"),
            ]
        else:  # Linux and other Unix-like systems
            return [
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                os.path.expanduser("~/.fonts"),
                os.path.expanduser("~/.local/share/fonts"),
            ]

    def find_font_in_system(self, font_name: str) -> Optional[str]:
        """Search for a font in system directories."""
        font_dirs = self.get_system_font_dirs()
        
        for font_dir in font_dirs:
            if not os.path.exists(font_dir):
                continue
                
            font_path = self._search_font_in_directory(font_dir, font_name)
            if font_path:
                return font_path
        return None

    def _search_font_in_directory(self, directory: str, font_name: str) -> Optional[str]:
        """Search for a font file in a specific directory and its subdirectories."""
        font_name_lower = font_name.lower().replace(" ", "")
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_lower = file.lower()
                if any(
                    font_name_lower in file_lower and file_lower.endswith(ext)
                    for ext in self.font_extensions
                ):
                    return os.path.join(root, file)
        return None

    def get_font_save_directory(self) -> str:
        """Get the appropriate directory for saving downloaded fonts."""
        if sys.platform == "win32":
            return os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
        elif sys.platform == "darwin":
            return os.path.expanduser("~/Library/Fonts")
        else:
            return os.path.expanduser("~/.local/share/fonts")

    def get_font_extension(self, content_type: str) -> str:
        """Determine font file extension based on content type."""
        if "woff2" in content_type:
            return ".woff2"
        elif "woff" in content_type:
            return ".woff"
        elif "opentype" in content_type:
            return ".otf"
        return ".ttf"  # Default to TTF

    def download_google_font(self, font_name: str) -> Optional[str]:
        """Download a font from Google Fonts."""
        try:
            api_font_name = font_name.replace(" ", "+")
            api_url = f"https://fonts.googleapis.com/css?family={api_font_name}"
            
            # Get the CSS containing the font file URL
            css_response = requests.get(api_url)
            if css_response.status_code != 200:
                if self.verbose:
                    print(f"Could not find font '{font_name}' on Google Fonts")
                return None
            
            font_url = self._extract_font_url(css_response.text)
            if not font_url:
                return None
            
            # Download the font file
            return self._save_font_file(font_name, font_url)
            
        except Exception as e:
            if self.verbose:
                print(f"Error downloading font: {e}")
            return None

    def _extract_font_url(self, css_content: str) -> Optional[str]:
        """Extract the font URL from Google Fonts CSS content."""
        url_start = css_content.find("url(") + 4
        url_end = css_content.find(")", url_start)
        
        if url_start < 4 or url_end < 0:
            if self.verbose:
                print("Could not parse font URL from Google Fonts CSS")
            return None
            
        return css_content[url_start:url_end]

    def _save_font_file(self, font_name: str, font_url: str) -> Optional[str]:
        """Download and save a font file from a URL."""
        try:
            font_response = requests.get(font_url)
            if font_response.status_code != 200:
                if self.verbose:
                    print(f"Failed to download font from {font_url}")
                return None
            
            # Determine save location and extension
            font_save_dir = self.get_font_save_directory()
            os.makedirs(font_save_dir, exist_ok=True)
            
            ext = self.get_font_extension(font_response.headers.get("Content-Type", ""))
            safe_font_name = font_name.replace(" ", "_")
            font_path = os.path.join(font_save_dir, f"{safe_font_name}{ext}")
            
            # Save the font file
            with open(font_path, "wb") as f:
                f.write(font_response.content)
            
            if self.verbose:
                print(f"Downloaded and saved font to: {font_path}")
            return font_path
            
        except Exception as e:
            if self.verbose:
                print(f"Error saving font file: {e}")
            return None

    def find_font(self, font_name: str) -> Optional[str]:
        """
        Search for a font on the system. If not found, attempt to download it from Google Fonts.
        
        Args:
            font_name: Name of the font to search for (e.g., "Roboto", "Open Sans")
            
        Returns:
            Path to the font file if found or downloaded successfully, None otherwise
        """
        # First try to find the font in the system
        font_path = self.find_font_in_system(font_name)
        if font_path:
            if self.verbose:
                print(f"Found font in system: {font_path}")
            return font_path
        
        # If not found, try to download from Google Fonts
        if self.verbose:
            print(f"Font '{font_name}' not found on system. Attempting to download...")
        return self.download_google_font(font_name)
