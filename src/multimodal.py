import base64
import io
import json
import mimetypes
import os
import re
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from urllib.request import urlopen
import requests
from PIL import Image
import fitz  # PyMuPDF for PDF processing

from .config import Config


class MultiModalProcessor:
    """Handles multi-modal input processing including images, documents, and text."""
    
    def __init__(self):
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.supported_document_formats = {'.pdf', '.txt', '.md', '.docx', '.doc'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.temp_dir = Path("temp_uploads")
        self.temp_dir.mkdir(exist_ok=True)
    
    def process_input(self, content: Union[str, Dict, List]) -> Dict[str, Any]:
        """Process multi-modal input and return structured data."""
        if isinstance(content, str):
            return self._process_text_input(content)
        elif isinstance(content, dict):
            return self._process_dict_input(content)
        elif isinstance(content, list):
            return self._process_list_input(content)
        else:
            raise ValueError(f"Unsupported input type: {type(content)}")
    
    def _process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input, detecting URLs, file paths, and base64 data."""
        result = {
            "type": "text",
            "content": text,
            "media": []
        }
        
        # Check for URLs
        urls = self._extract_urls(text)
        for url in urls:
            media_item = self._process_url(url)
            if media_item:
                result["media"].append(media_item)
        
        # Check for file paths
        file_paths = self._extract_file_paths(text)
        for file_path in file_paths:
            media_item = self._process_file_path(file_path)
            if media_item:
                result["media"].append(media_item)
        
        # Check for base64 encoded data
        base64_data = self._extract_base64(text)
        for b64_item in base64_data:
            media_item = self._process_base64(b64_item)
            if media_item:
                result["media"].append(media_item)
        
        return result
    
    def _process_dict_input(self, data: Dict) -> Dict[str, Any]:
        """Process dictionary input with potential media fields."""
        result = {
            "type": "mixed",
            "content": data.get("text", ""),
            "media": []
        }
        
        # Process text content
        if "text" in data:
            text_result = self._process_text_input(data["text"])
            result["content"] = text_result["content"]
            result["media"].extend(text_result["media"])
        
        # Process image fields
        for field in ["image", "images", "file", "files"]:
            if field in data:
                media_items = self._process_media_field(data[field])
                result["media"].extend(media_items)
        
        return result
    
    def _process_list_input(self, data: List) -> Dict[str, Any]:
        """Process list input as mixed content."""
        result = {
            "type": "mixed",
            "content": "",
            "media": []
        }
        
        for item in data:
            if isinstance(item, str):
                # Process text items
                text_result = self._process_text_input(item)
                if text_result["content"]:
                    result["content"] += text_result["content"] + "\n"
                result["media"].extend(text_result["media"])
            elif isinstance(item, dict):
                # Process media items
                media_item = self._process_dict_input(item)
                if media_item["content"]:
                    result["content"] += media_item["content"] + "\n"
                result["media"].extend(media_item["media"])
        
        return result
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    def _extract_file_paths(self, text: str) -> List[str]:
        """Extract file paths from text."""
        # Simple file path pattern - can be enhanced
        file_pattern = r'[\w\-./\\]+\.(?:jpg|jpeg|png|gif|bmp|webp|pdf|txt|md|docx?)$'
        return re.findall(file_pattern, text, re.IGNORECASE)
    
    def _extract_base64(self, text: str) -> List[Dict[str, str]]:
        """Extract base64 encoded data from text."""
        base64_pattern = r'data:([^;]+);base64,([A-Za-z0-9+/=]+)'
        matches = re.findall(base64_pattern, text)
        return [{"mime_type": mime, "data": data} for mime, data in matches]
    
    def _process_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Process URL to determine if it's an image or document."""
        try:
            # Check if it's an image URL
            if any(ext in url.lower() for ext in self.supported_image_formats):
                return {
                    "type": "image",
                    "source": "url",
                    "url": url,
                    "mime_type": self._get_mime_type_from_url(url)
                }
            
            # Check if it's a document URL
            if any(ext in url.lower() for ext in self.supported_document_formats):
                return {
                    "type": "document",
                    "source": "url",
                    "url": url,
                    "mime_type": self._get_mime_type_from_url(url)
                }
            
            # Try to fetch and determine type
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            
            if 'image' in content_type:
                return {
                    "type": "image",
                    "source": "url",
                    "url": url,
                    "mime_type": content_type
                }
            elif 'pdf' in content_type or 'document' in content_type:
                return {
                    "type": "document",
                    "source": "url",
                    "url": url,
                    "mime_type": content_type
                }
            
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
        
        return None
    
    def _process_file_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process local file path."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            if path.stat().st_size > self.max_file_size:
                print(f"File {file_path} is too large")
                return None
            
            suffix = path.suffix.lower()
            
            if suffix in self.supported_image_formats:
                return {
                    "type": "image",
                    "source": "file",
                    "path": str(path),
                    "mime_type": mimetypes.guess_type(str(path))[0]
                }
            elif suffix in self.supported_document_formats:
                return {
                    "type": "document",
                    "source": "file",
                    "path": str(path),
                    "mime_type": mimetypes.guess_type(str(path))[0]
                }
            
        except Exception as e:
            print(f"Error processing file path {file_path}: {e}")
        
        return None
    
    def _process_base64(self, b64_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process base64 encoded data."""
        try:
            mime_type = b64_data["mime_type"]
            data = b64_data["data"]
            
            # Decode base64
            decoded_data = base64.b64decode(data)
            
            if 'image' in mime_type:
                # Save image to temp file
                temp_path = self.temp_dir / f"temp_image_{hash(data) % 10000}.png"
                with open(temp_path, 'wb') as f:
                    f.write(decoded_data)
                
                return {
                    "type": "image",
                    "source": "base64",
                    "path": str(temp_path),
                    "mime_type": mime_type
                }
            elif 'pdf' in mime_type or 'document' in mime_type:
                # Save document to temp file
                temp_path = self.temp_dir / f"temp_doc_{hash(data) % 10000}.pdf"
                with open(temp_path, 'wb') as f:
                    f.write(decoded_data)
                
                return {
                    "type": "document",
                    "source": "base64",
                    "path": str(temp_path),
                    "mime_type": mime_type
                }
            
        except Exception as e:
            print(f"Error processing base64 data: {e}")
        
        return None
    
    def _process_media_field(self, media_data: Any) -> List[Dict[str, Any]]:
        """Process media field from input data."""
        media_items = []
        
        if isinstance(media_data, str):
            # Single media item
            item = self._process_url(media_data) or self._process_file_path(media_data)
            if item:
                media_items.append(item)
        elif isinstance(media_data, list):
            # Multiple media items
            for item in media_data:
                if isinstance(item, str):
                    media_item = self._process_url(item) or self._process_file_path(item)
                    if media_item:
                        media_items.append(media_item)
                elif isinstance(item, dict):
                    # Handle dict format media items
                    media_items.append(item)
        
        return media_items
    
    def _get_mime_type_from_url(self, url: str) -> str:
        """Get MIME type from URL extension."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lower()
        
        if any(ext in path for ext in ['.jpg', '.jpeg']):
            return 'image/jpeg'
        elif '.png' in path:
            return 'image/png'
        elif '.gif' in path:
            return 'image/gif'
        elif '.webp' in path:
            return 'image/webp'
        elif '.pdf' in path:
            return 'application/pdf'
        elif '.txt' in path:
            return 'text/plain'
        elif '.md' in path:
            return 'text/markdown'
        else:
            return 'application/octet-stream'
    
    def extract_text_from_document(self, file_path: str) -> str:
        """Extract text from various document formats."""
        try:
            path = Path(file_path)
            suffix = path.suffix.lower()
            
            if suffix == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif suffix in ['.txt', '.md']:
                return self._extract_text_from_text_file(file_path)
            elif suffix in ['.docx', '.doc']:
                return self._extract_text_from_word(file_path)
            else:
                return f"Unsupported document format: {suffix}"
                
        except Exception as e:
            return f"Error extracting text from document: {e}"
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {e}"
    
    def _extract_text_from_text_file(self, file_path: str) -> str:
        """Extract text from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading text file: {e}"
    
    def _extract_text_from_word(self, file_path: str) -> str:
        """Extract text from Word document."""
        try:
            # This would require python-docx library
            # For now, return a placeholder
            return f"Word document processing not yet implemented: {file_path}"
        except Exception as e:
            return f"Error extracting text from Word document: {e}"
    
    def process_image_for_analysis(self, image_path: str) -> Dict[str, Any]:
        """Process image for analysis and return metadata."""
        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "path": image_path
                }
        except Exception as e:
            return {"error": f"Error processing image: {e}"}
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")


class MultiModalResponse:
    """Handles multi-modal response generation and formatting."""
    
    def __init__(self):
        self.processor = MultiModalProcessor()
    
    def format_response(self, content: str, media: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format response with text and media content."""
        response = {
            "content": content,
            "media": media or [],
            "ui_signal": self._generate_ui_signals(media) if media else None
        }
        return response
    
    def _generate_ui_signals(self, media: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate UI signals for media content."""
        signals = {
            "type": "multimodal_response",
            "media_count": len(media),
            "actions": []
        }
        
        for item in media:
            if item["type"] == "image":
                signals["actions"].append({
                    "type": "display_image",
                    "source": item["source"],
                    "path": item.get("path"),
                    "url": item.get("url")
                })
            elif item["type"] == "document":
                signals["actions"].append({
                    "type": "display_document",
                    "source": item["source"],
                    "path": item.get("path"),
                    "url": item.get("url")
                })
        
        return signals


# Global instances
multimodal_processor = MultiModalProcessor()
multimodal_response = MultiModalResponse() 