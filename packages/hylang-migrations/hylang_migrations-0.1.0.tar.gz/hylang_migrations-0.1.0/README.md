# Pure Hylang Migration Tool

A **100% pure Hylang v1.1.0** schema migration tool for SQLite with SQLObject integration. No Python code - everything is written in idiomatic Hylang using modern features like `hyrule` macros.

## Features

- ✨ **Pure Hylang** - Entire codebase in Hylang v1.1.0, no Python files
- 🎯 **Modern Hylang idioms** - Uses `hyrule` macros, `let` bindings, and functional patterns
- 📦 **Pip installable** - Works as a standard Python package despite being pure Hylang
- 🔄 **Full migration lifecycle** - Create, apply, rollback, validate migrations
- 🗃️ **SQLObject integration** - Seamless ORM support
- 🎨 **Colored CLI output** - Beautiful terminal interface using colorama
- 🛡️ **Transaction safety** - All migrations run in transactions
- ✅ **Validation & checksums** - Ensure migration integrity
- 🔍 **Dry-run mode** - Preview changes before applying

## Installation

### Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager that provides excellent environment handling:

```bash
# Clone the repository
git clone https://github.com/yourusername/hylang-migrations.git
cd hylang-migrations

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# The tool is now available
hylang-migrate --help
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/hylang-migrations.git
cd hylang-migrations

# Install in development mode
pip install -e .

# Or build and install
pip install build
python -m build
pip install dist/hylang_migrations-*.whl
```

### From PyPI (when published)

```bash
pip install hylang-migrations
```

## Quick Start

### 1. Initialize Your Project

```bash
cd your-project
hylang-migrate init
```

This creates:
- `migrations/` directory for migration files
- `.migrations` configuration file (in Hylang format)
- Initial project structure

### 2. Create a Migration

```bash
hylang-migrate create create_users_table
```

This generates a timestamped Hylang migration file:

```hylang
;;; Migration: create_users_table
;;; Version: 20240101120000

(defclass CreateUsersTable []
  (defn up [self connection]
    "Apply migration"
    (connection.execute
      "CREATE TABLE users (
         id INTEGER PRIMARY KEY,
         username VARCHAR(255) UNIQUE NOT NULL,
         email VARCHAR(255) UNIQUE NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )"))
  
  (defn down [self connection]
    "Rollback migration"
    (connection.execute "DROP TABLE IF EXISTS users")))

(setv migration (CreateUsersTable))
```

### 3. Run Migrations

```bash
# Apply all pending migrations
hylang-migrate migrate

# Preview changes (dry run)
hylang-migrate migrate --dry-run

# Migrate to specific version
hylang-migrate migrate --target 20240101120000
```

### 4. Check Status

```bash
hylang-migrate status
```

Output:
```
📊 Migration Status
  Database: database.db
  Migrations: migrations/

✅ Applied Migrations:
Version          Name                    Applied At
20240101120000   create_users_table     2024-01-01 12:00:00

⏳ Pending Migrations:
Version          Name
20240101130000   add_user_profiles
```

### 5. Rollback

```bash
# Rollback last migration
hylang-migrate rollback

# Rollback multiple migrations
hylang-migrate rollback --steps 3

# Rollback to specific version
hylang-migrate rollback --to 20240101120000
```

## Command Reference

### Global Options

- `--config PATH` - Configuration file path (default: `.migrations`)
- `--db PATH` - Database file path (default: `database.db`)
- `--migrations-dir PATH` - Migrations directory (default: `migrations`)
- `--verbose` - Verbose output

### Commands

| Command | Description | Options |
|---------|-------------|---------|
| `init` | Initialize migration system | - |
| `create NAME` | Create new migration | - |
| `migrate` | Run pending migrations | `--target VERSION`, `--dry-run` |
| `rollback` | Rollback migrations | `--steps N`, `--to VERSION`, `--dry-run` |
| `status` | Show migration status | - |
| `list` | List all migrations | `--pending`, `--applied` |
| `show VERSION` | Show migration details | - |
| `validate` | Validate migration files | - |

## Configuration

### Hylang Format (`.migrations`)

```hylang
{
  :database {
    :path "database.db"
    :type "sqlite"
  }
  :migrations {
    :directory "migrations"
    :table-name "migration_history"
    :auto-transaction true
    :verify-checksums true
  }
  :sqlobject {
    :debug false
    :cache true
    :lazy-update true
  }
  :logging {
    :level "INFO"
    :file "migrations.log"
  }
}
```

### Environment Variables

```bash
export DB_PATH=production.db
export MIGRATIONS_DIR=db/migrations
export SQLOBJECT_DEBUG=true
```

## Writing Migrations

### Basic Migration Structure

```hylang
(require hyrule [-> ->> as->])
(import sqlite3)

(defclass MigrationName []
  (defn __init__ [self]
    (setv self.version "20240101120000")
    (setv self.name "migration_name"))
  
  (defn up [self connection]
    "Apply migration"
    ;; Your forward migration logic
    )
  
  (defn down [self connection]
    "Rollback migration"
    ;; Your rollback logic
    )
  
  (defn validate [self connection]
    "Optional validation"
    True)
  
  (defn get-checksum [self]
    "Calculate checksum"
    (import hashlib)
    (-> (hashlib.sha256)
        (.update (.encode (+ self.version self.name) "utf-8"))
        (.hexdigest))))

(setv migration (MigrationName))
```

### Using SQLObject Models

```hylang
(import sqlobject [SQLObject StringCol IntCol DateTimeCol BoolCol])
(import datetime [datetime])

(defclass User [SQLObject]
  (setv _table "users")
  (setv username (StringCol :unique True :notNone True))
  (setv email (StringCol :unique True :notNone True))
  (setv is-active (BoolCol :default True))
  (setv created-at (DateTimeCol :default datetime.now)))
```

## Pure Hylang Implementation

This tool is written entirely in Hylang v1.1.0 with modern idioms:

### Key Files (all `.hy`):

- `cli.hy` - Command-line interface with argparse and colorama
- `migrations.hy` - Core migration engine
- `config.hy` - Configuration management
- `utils.hy` - Utility functions
- `templates.hy` - Migration and model generators

### Hylang v1.1.0 Features Used:

- `require hyrule` for modern macros
- `let` bindings for local scope
- `lfor` list comprehensions
- `#**` for keyword arguments
- f-strings for formatting
- Pattern matching with `cond`

## Development

### Setup Development Environment

```bash
# Clone repo
git clone https://github.com/yourusername/hylang-migrations.git
cd hylang-migrations

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_migrations.hy

# With coverage
pytest --cov=hylang_migrations tests/
```

### Building Package

```bash
# Build distribution
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## Project Structure

```
hylang-migrations/
├── src/
│   └── hylang_migrations/
│       ├── __init__.hy          # Package initialization
│       ├── __main__.hy          # Module entry point
│       ├── cli.hy               # CLI implementation
│       ├── migrations.hy        # Core engine
│       ├── config.hy            # Configuration
│       ├── utils.hy             # Utilities
│       └── templates.hy         # Generators
├── migrations/                   # User migrations directory
│   └── *.hy                     # Migration files
├── tests/                       # Test suite
│   └── test_*.hy               # Test files
├── pyproject.toml              # Package configuration
├── setup.hy                    # Hylang setup script
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## Why Pure Hylang?

This project demonstrates that complex tools can be written entirely in Hylang without any Python code:

1. **Language Purity** - Shows Hylang's completeness as a language
2. **Lisp Power** - Leverages macros and functional programming
3. **Python Ecosystem** - Still integrates seamlessly with pip/PyPI
4. **Modern Hylang** - Uses latest v1.1.0 features and idioms
5. **Real-World Tool** - Not just a toy, but a production-ready tool

## Claude Code Integration

This package includes Claude Code subagents to help you work with Hylang migrations more effectively!

### Installing Claude Agents

```bash
# Install the Hylang migrations assistant
hylang-migrate install-claude-agent

# The agents are now available in Claude Code!
```

### Available Agents

1. **hylang-migrate-assistant** - Expert help with:
   - Creating and managing migrations
   - Debugging migration issues  
   - Schema design best practices
   - Hylang v1.1.0 migration syntax

2. **hyrule-expert** - Hylang/Hyrule language expert for:
   - Conditionals (`if`, `when`, `cond`)
   - Loops and comprehensions
   - String formatting (`.format` vs f-strings)
   - Hyrule macros and utilities

To use these agents in Claude Code, type `/agents` and select the appropriate assistant.

## Contributing

Contributions must be in pure Hylang! We welcome:

- Bug fixes
- New features
- Documentation improvements
- Test coverage
- Performance optimizations

Please ensure all code follows Hylang v1.1.0 idioms and includes tests.

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Hylang community for the amazing Lisp-on-Python language
- SQLObject for the ORM functionality
- All contributors to the Python ecosystem

---

**Remember**: This entire tool is written in pure Hylang - no Python files! 🎉
