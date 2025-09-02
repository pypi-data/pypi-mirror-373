"""
ATX Mainframe BRE Analyzer - Business Rules Extraction Analysis Server
Provides structured analysis of ATX Business Rules Extraction output for mainframe modernization.
"""

__version__ = "0.1.0"

def main():
    """Main entry point for the CLI."""
    import asyncio
    from .server import main as server_main
    asyncio.run(server_main())