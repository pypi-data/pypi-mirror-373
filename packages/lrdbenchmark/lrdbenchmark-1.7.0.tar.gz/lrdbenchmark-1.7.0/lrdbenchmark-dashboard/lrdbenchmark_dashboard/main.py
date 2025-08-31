#!/usr/bin/env python3
"""
Main entry point for LRDBenchmark Dashboard
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """
    Main function to run the LRDBenchmark Dashboard
    """
    try:
        # Get the path to the app.py file
        package_dir = Path(__file__).parent
        app_path = package_dir / "app.py"
        
        if not app_path.exists():
            print(f"Error: Dashboard app not found at {app_path}")
            sys.exit(1)
        
        # Run the Streamlit app
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(app_path), 
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ]
        
        print("🚀 Starting LRDBenchmark Dashboard...")
        print(f"📊 Dashboard will be available at: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the dashboard")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
