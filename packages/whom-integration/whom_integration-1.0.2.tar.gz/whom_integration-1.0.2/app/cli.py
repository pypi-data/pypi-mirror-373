#!/usr/bin/env python3
"""
Command Line Interface for Whom Integration Library
"""

import argparse
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import WhomClient, ECACSystem, PJESystem, SeleniumDriver, PlaywrightDriver


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Whom Integration Library - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test ECAC with Playwright
  whom-integration --system ecac --driver playwright --token YOUR_TOKEN --extension YOUR_EXTENSION

  # Test PJE with Selenium
  whom-integration --system pje --driver selenium --token YOUR_TOKEN --extension YOUR_EXTENSION

  # Show version
  whom-integration --version
        """
    )

    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0"
    )

    parser.add_argument(
        "--system",
        choices=["ecac", "pje"],
        help="Target system to integrate with"
    )

    parser.add_argument(
        "--driver",
        choices=["selenium", "playwright"],
        help="Automation driver to use"
    )

    parser.add_argument(
        "--token",
        help="Whom API authentication token"
    )

    parser.add_argument(
        "--extension",
        help="Whom extension ID"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for operations (default: 30)"
    )

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Validate required arguments
    if args.system and not args.driver:
        parser.error("--driver is required when --system is specified")
    
    if args.driver and not args.system:
        parser.error("--system is required when --driver is specified")

    if args.system and args.driver and not args.token:
        parser.error("--token is required for system integration")

    if args.system and args.driver and not args.extension:
        parser.error("--extension is required for system integration")

    # Execute integration if all required args are provided
    if all([args.system, args.driver, args.token, args.extension]):
        execute_integration(args)
    else:
        parser.print_help()


def execute_integration(args):
    """Execute the integration based on CLI arguments"""
    try:
        print(f"🚀 Starting {args.system.upper()} integration with {args.driver.title()}")
        print("=" * 60)

        # Create client
        client = WhomClient(args.token, args.extension)

        # Select system and driver classes
        system_map = {
            "ecac": ECACSystem,
            "pje": PJESystem
        }

        driver_map = {
            "selenium": SeleniumDriver,
            "playwright": PlaywrightDriver
        }

        system_class = system_map[args.system]
        driver_class = driver_map[args.driver]

        # Configuration
        config = {
            "headless": args.headless,
            "timeout": args.timeout
        }

        # Add driver-specific config
        if args.driver == "selenium":
            config["window_size"] = (1920, 1080)
        elif args.driver == "playwright":
            config["viewport"] = {"width": 1920, "height": 1080}

        # Create and execute session
        with client.create_session(system_class, driver_class, **config) as session:
            print("✅ Session created successfully")
            
            # Authenticate
            print("🔐 Authenticating...")
            session.authenticate_and_connect()
            
            # Execute workflow
            print("⚙️ Executing default workflow...")
            result = session.execute_workflow("default")
            
            print(f"\n🎯 Result: {result}")
            print("✅ Integration completed successfully!")
            input("Press Enter to continue...")

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during integration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
