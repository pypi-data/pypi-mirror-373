#!/usr/bin/env python3
"""
Build and upload script for LRDBenchmark Dashboard PyPI package
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    """Main build and upload process"""
    print("🚀 LRDBenchmark Dashboard - Build and Upload to PyPI")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ Error: setup.py not found. Please run this script from the lrdbenchmark-dashboard directory.")
        sys.exit(1)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    run_command("python -m build --clean", "Cleaning build artifacts")
    
    # Build the package
    print("🔨 Building package...")
    run_command("python -m build", "Building package")
    
    # Check the built package
    print("🔍 Checking built package...")
    run_command("python -m twine check dist/*", "Checking package")
    
    # Ask user if they want to upload to PyPI
    print("\n📦 Package built successfully!")
    print("📁 Built files:")
    dist_files = list(Path("dist").glob("*"))
    for file in dist_files:
        print(f"   - {file.name}")
    
    print("\n🚀 Upload options:")
    print("1. Upload to PyPI (production)")
    print("2. Upload to TestPyPI (testing)")
    print("3. Exit without uploading")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("⚠️  WARNING: This will upload to PyPI (production)")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            run_command("python -m twine upload dist/*", "Uploading to PyPI")
            print("🎉 Successfully uploaded to PyPI!")
            print("📦 Package available at: https://pypi.org/project/lrdbenchmark-dashboard/")
        else:
            print("❌ Upload cancelled")
    elif choice == "2":
        print("🧪 Uploading to TestPyPI...")
        run_command("python -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI")
        print("🎉 Successfully uploaded to TestPyPI!")
        print("📦 Package available at: https://test.pypi.org/project/lrdbenchmark-dashboard/")
    else:
        print("❌ Upload cancelled")
    
    print("\n✅ Build process completed!")

if __name__ == "__main__":
    main()
