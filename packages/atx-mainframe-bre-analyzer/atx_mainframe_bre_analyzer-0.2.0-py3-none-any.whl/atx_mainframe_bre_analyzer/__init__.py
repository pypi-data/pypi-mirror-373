"""
ATX Mainframe BRE Analyzer - Business Rules Extraction Analysis Server
Provides structured analysis of ATX Business Rules Extraction output for mainframe modernization.
"""

__version__ = "0.2.0"

def main():
    """Main entry point for the CLI."""
    from .server import main as server_main
    server_main()