#!/usr/bin/env python3

"""
Main entry point for Aider-Jac-OSP
"""

import sys
import os

def main():
    """Main entry point"""
    try:
        from .cli import main as genius_main
        
        # Simple argument parsing to determine mode
        if len(sys.argv) > 1 and sys.argv[1] == '--help':
            print("Aider-Jac-OSP v2.0.0 - AI Pair Programming Assistant")
            print("")
            print("usage: aider [options] [files...]")
            print("")
            print("Enhanced AI pair programming in your terminal with Jac-OSP integration")
            print("")
            print("options:")
            print("  -h, --help           show this help message and exit")
            print("  --genius-mode        enable genius mode for advanced capabilities")
            print("  --jac                enable Jac Object-Spatial Programming mode")
            print("  --model MODEL        specify the AI model to use")
            print("  --version            show version and exit")
            print("")
            print("For full functionality and advanced features:")
            print("  aider-genius --help")
            print("")
            return 0
        elif len(sys.argv) > 1 and 'genius' in ' '.join(sys.argv):
            # Redirect to genius mode
            return genius_main()
        elif len(sys.argv) > 1 and sys.argv[1] == '--version':
            print("aider-jac-osp 2.0.0")
            return 0
        else:
            # Basic help for now
            print("Aider-Jac-OSP v2.0.0 - AI Pair Programming Assistant")
            print("")
            print("Available commands:")
            print("  aider-genius    - Advanced AI coding assistant")
            print("  aider --help    - Show detailed help")
            print("")
            print("For full functionality, use: aider-genius")
            return 0
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

if __name__ == "__main__":
    main()