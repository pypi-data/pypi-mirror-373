#!/usr/bin/env python3
"""
Main entry point for League Analysis MCP Server package.

This allows the package to be run directly with:
- uvx league-analysis-mcp-server
- python -m league_analysis_mcp_server
"""

import sys
import logging

def main():
    """Main entry point for the package."""
    try:
        # Configure logging for package execution
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Import and run the server
        from .server import main as server_main
        return server_main()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except ImportError as e:
        print(f"Failed to import server components: {e}")
        print("Make sure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Failed to start League Analysis MCP Server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())