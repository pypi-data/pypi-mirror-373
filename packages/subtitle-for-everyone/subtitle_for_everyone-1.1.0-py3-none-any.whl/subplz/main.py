#!/usr/bin/env python3
"""
SubPlz Enhanced CLI Entry Point
Provides both traditional CLI and modern TUI interfaces
"""

import sys
import argparse
from .pipeline import main as cli_main
from .tui import run_tui


def main():
    """Main entry point that routes to CLI or TUI"""
    parser = argparse.ArgumentParser(
        description="SubPlz - Subtitle Pipeline for Everyone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Interface Options:
  --tui           Launch interactive terminal interface (default)
  --cli           Use traditional command-line interface
  
CLI Mode Examples:
  subplz --cli https://www.youtube.com/watch?v=VIDEO_ID
  subplz --cli /path/to/local/video.mp4
  subplz --cli "C:\\Users\\Name\\Videos\\myvideo.mp4"

TUI Mode:
  subplz          Launch interactive interface
  subplz --tui    Launch interactive interface
        """
    )
    
    # Interface selection
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument(
        "--tui", 
        action="store_true",
        help="Launch interactive terminal user interface (default)"
    )
    interface_group.add_argument(
        "--cli", 
        action="store_true",
        help="Use traditional command-line interface"
    )
    
    # CLI-specific arguments
    parser.add_argument(
        "source",
        nargs="?",
        help="YouTube URL or path to local video file (required for CLI mode)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory for CLI mode"
    )
    
    args = parser.parse_args()
    
    # Determine which interface to use
    if args.cli:
        # Traditional CLI mode
        if not args.source:
            parser.error("source is required when using --cli mode")
        
        # Set up sys.argv for the original CLI
        cli_args = ["subplz", args.source]
        if args.output:
            cli_args.extend(["-o", args.output])
        
        sys.argv = cli_args
        return cli_main()
    
    else:
        # TUI mode (default)
        if args.source:
            print("Note: source argument ignored in TUI mode. Use the interface to select files.")
        
        try:
            run_tui()
            return 0
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0
        except Exception as e:
            print(f"TUI Error: {e}")
            print("Falling back to CLI mode. Run with --cli for traditional interface.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
