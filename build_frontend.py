#!/usr/bin/env uv run
"""
Frontend Build Script

This script builds the frontend and copies the result to the static directory
for serving with the FastAPI backend.
"""

import os
import subprocess
import shutil
import sys

def main():
    """Build frontend and copy to static directory."""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    static_dir = os.path.join(project_root, "static")
    
    print("🔨 Building frontend...")
    
    # Check if frontend directory exists
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found!")
        print(f"   Expected: {frontend_dir}")
        sys.exit(1)
    
    # Change to frontend directory and build
    try:
        os.chdir(frontend_dir)
        
        # Install dependencies if needed
        if not os.path.exists("node_modules"):
            print("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Build the frontend
        print("🏗️  Building frontend with Webpack...")
        subprocess.run(["npm", "run", "build"], check=True)
        
        # Go back to project root
        os.chdir(project_root)
        
        # Create static directory if it doesn't exist
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            print(f"📁 Created static directory: {static_dir}")
        
        # Copy built files to static directory
        frontend_dist = os.path.join(frontend_dir, "dist")
        if os.path.exists(frontend_dist):
            print("📋 Copying built files to static directory...")
            
            # Clear existing static directory
            if os.path.exists(static_dir):
                shutil.rmtree(static_dir)
                os.makedirs(static_dir)
            
            # Copy all files from dist to static
            shutil.copytree(frontend_dist, static_dir, dirs_exist_ok=True)
            
            print("✅ Frontend built and copied successfully!")
            print(f"📁 Static files location: {static_dir}")
            print(f"🌐 Ready to serve with: python main.py --mode frontend")
            
        else:
            print("❌ Frontend build failed - dist directory not found")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 