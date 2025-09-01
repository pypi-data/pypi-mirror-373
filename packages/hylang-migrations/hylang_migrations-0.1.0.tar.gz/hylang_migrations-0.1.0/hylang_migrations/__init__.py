"""
Hylang Migrations - Pure Hylang database migration tool for SQLite

A schema versioning and migration management system written entirely in Hylang (Lisp for Python).
"""

__version__ = "0.1.0"
__author__ = "James"
__email__ = "james@example.com"

# Import Hy to enable .hy file imports
import hy

# Import main components from Hy modules
# These will be available after Hy processes the .hy files
try:
    from .migrations import Migration, MigrationHistory, MigrationRunner
    from .config import Config
    from .cli import main as cli_main
    
    __all__ = [
        "Migration",
        "MigrationHistory", 
        "MigrationRunner",
        "Config",
        "cli_main",
        "__version__",
    ]
except ImportError as e:
    # During package building, imports might fail
    # This is expected and doesn't affect the installed package
    import warnings
    warnings.warn(f"Could not import Hy modules during build: {e}", ImportWarning)