#!/usr/bin/env python3
"""
BioXen-luavm CLI Entry Point
Provides the main entry point for the interactive CLI.
"""

import sys
import os

# Add the current directory to the path to allow importing the CLI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the CLI"""
    try:
        # Import the CLI module from the root directory
        import sys
        import os
        
        # Get the parent directory (project root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Import and run the CLI
        from interactive_bioxen_lua import BioXenLuavmCLI
        
        cli = BioXenLuavmCLI()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Exiting BioXen-luavm...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
