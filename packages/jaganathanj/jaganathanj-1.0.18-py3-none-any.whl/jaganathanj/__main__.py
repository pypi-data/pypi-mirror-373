# jaganathanj/__main__.py
"""
Entry point for running jaganathanj as a module.
Supports both 'python -m jaganathanj' and direct script execution.
"""

import sys
import os

# Add the package directory to the path if running as script
if __name__ == "__main__":
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Add to Python path if not already there
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Import and run the CLI main function
try:
    from .cli import main
except ImportError:
    # Fallback for direct script execution
    from cli import main

if __name__ == "__main__":
    main()