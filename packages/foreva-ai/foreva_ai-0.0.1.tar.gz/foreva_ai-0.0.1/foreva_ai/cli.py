"""
Foreva AI SDK Command Line Interface
"""

import sys
import argparse
from . import __version__

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='foreva',
        description='Foreva AI SDK Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  foreva --version                    Show SDK version
  foreva --help                       Show this help message

For SDK usage, see: https://docs.foreva.ai/sdk/python
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'foreva-ai {__version__}'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show SDK information and links'
    )
    
    args = parser.parse_args()
    
    if args.info:
        print(f"Foreva AI Python SDK v{__version__}")
        print()
        print("🔗 Documentation: https://docs.foreva.ai/sdk/python")
        print("🔑 Get API Keys: https://foreva.ai/partners/dashboard/")
        print("💬 Support: https://foreva.ai/support/")
        print("🐛 Issues: https://github.com/foreva-ai/python-sdk/issues")
        print()
        print("Quick Start:")
        print("  from foreva_ai import ForevaAgent")
        print("  agent = ForevaAgent('your_api_key', 'your_phone_number')")
        print()
        return 0
    
    # If no arguments, show help
    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())