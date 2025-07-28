#!/usr/bin/env python3
"""
Test script for the Multi-Modal functionality
"""

import requests
import json
import time
import base64
from pathlib import Path


def test_multimodal_processing():
    """Test multi-modal input processing."""
    print("Testing multi-modal input processing...")
    try:
        # Test text with URL
        test_content = "Check out this image: https://example.com/image.jpg"
        response = requests.post("http://localhost:8002/multimodal/process", json={"content": test_content})
        
        if response.status_code == 200:
            print("✅ Multi-modal processing test passed")
            result = response.json()
            print(f"Processed content: {result['content']}")
            print(f"Media items: {len(result['media'])}")
        else:
            print(f"❌ Multi-modal processing test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Multi-modal processing test error: {e}")


def test_multimodal_chat():
    """Test multi-modal chat functionality."""
    print("\nTesting multi-modal chat...")
    try:
        # Test chat with multi-modal input
        response = requests.post("http://localhost:8002/chat", json={
            "messages": [
                {"role": "user", "content": "Analyze this image: https://example.com/image.jpg"}
            ],
            "multimodal": True
        })
        
        if response.status_code == 200:
            print("✅ Multi-modal chat test passed")
            result = response.json()
            print(f"Response: {result['content'][:100]}...")
            if result.get('media'):
                print(f"Response media: {len(result['media'])} items")
        else:
            print(f"❌ Multi-modal chat test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Multi-modal chat test error: {e}")


def test_document_text_extraction():
    """Test document text extraction."""
    print("\nTesting document text extraction...")
    try:
        # Create a simple test file
        test_file = Path("test_document.txt")
        test_content = "This is a test document for text extraction."
        test_file.write_text(test_content)
        
        response = requests.post("http://localhost:8002/multimodal/extract-text", 
                               params={"file_path": str(test_file)})
        
        if response.status_code == 200:
            print("✅ Document text extraction test passed")
            result = response.json()
            print(f"Extracted text: {result['extracted_text']}")
        else:
            print(f"❌ Document text extraction test failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Clean up test file
        test_file.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Document text extraction test error: {e}")


def test_image_analysis():
    """Test image analysis functionality."""
    print("\nTesting image analysis...")
    try:
        # Create a simple test image (1x1 pixel PNG)
        test_image = Path("test_image.png")
        png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        test_image.write_bytes(png_data)
        
        response = requests.post("http://localhost:8002/multimodal/analyze-image", 
                               params={"image_path": str(test_image)})
        
        if response.status_code == 200:
            print("✅ Image analysis test passed")
            result = response.json()
            print(f"Image metadata: {result['metadata']}")
        else:
            print(f"❌ Image analysis test failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Clean up test file
        test_image.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Image analysis test error: {e}")


def test_file_upload():
    """Test file upload functionality."""
    print("\nTesting file upload...")
    try:
        # Create a test file
        test_file = Path("test_upload.txt")
        test_content = "This is a test file for upload."
        test_file.write_text(test_content)
        
        # Upload the file
        with open(test_file, "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post("http://localhost:8002/multimodal/upload", files=files)
        
        if response.status_code == 200:
            print("✅ File upload test passed")
            result = response.json()
            print(f"Uploaded file info: {result}")
        else:
            print(f"❌ File upload test failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Clean up test file
        test_file.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ File upload test error: {e}")


def test_cleanup():
    """Test cleanup functionality."""
    print("\nTesting cleanup...")
    try:
        response = requests.delete("http://localhost:8002/multimodal/cleanup")
        
        if response.status_code == 200:
            print("✅ Cleanup test passed")
            result = response.json()
            print(f"Cleanup result: {result}")
        else:
            print(f"❌ Cleanup test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Cleanup test error: {e}")


def test_base64_processing():
    """Test base64 data processing."""
    print("\nTesting base64 processing...")
    try:
        # Create base64 encoded image data
        png_data = base64.b64encode(b"fake_png_data").decode()
        base64_content = f"data:image/png;base64,{png_data}"
        
        response = requests.post("http://localhost:8002/multimodal/process", json={"content": base64_content})
        
        if response.status_code == 200:
            print("✅ Base64 processing test passed")
            result = response.json()
            print(f"Base64 processing result: {result}")
        else:
            print(f"❌ Base64 processing test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Base64 processing test error: {e}")


def main():
    """Run all multi-modal tests."""
    print("🚀 Starting Multi-Modal Tests")
    print("=" * 50)
    
    # Wait a moment for the server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_multimodal_processing()
    test_multimodal_chat()
    test_document_text_extraction()
    test_image_analysis()
    test_file_upload()
    test_base64_processing()
    test_cleanup()
    
    print("\n" + "=" * 50)
    print("🏁 Multi-modal tests completed!")


if __name__ == "__main__":
    main() 