# Morpheus

A powerful DAG-based migration system for Neo4j graph databases with support for parallel execution, dependency management, and automatic conflict detection.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Using uv](#using-uv-recommended)
  - [Using pip](#using-pip)
  - [From source](#from-source)
- [Quick Start](#quick-start)
  - [1. Initialize Migration System](#1-initialize-migration-system)
  - [2. Configure Database Connection](#2-configure-database-connection)
  - [3. Create Your First Migration](#3-create-your-first-migration)
  - [4. Apply Migrations](#4-apply-migrations)
- [CLI Commands](#cli-commands)
  - [`morpheus init`](#morpheus-init)
  - [`morpheus create`](#morpheus-create)
  - [`morpheus status`](#morpheus-status)
  - [`morpheus upgrade`](#morpheus-upgrade)
  - [`morpheus downgrade`](#morpheus-downgrade)
  - [`morpheus dag`](#morpheus-dag)
- [Advanced Features](#advanced-features)
  - [Dependency Management](#dependency-management)
  - [Conflict Detection](#conflict-detection)
  - [Priority Levels](#priority-levels)
  - [Tag System](#tag-system)
  - [Parallel Execution](#parallel-execution)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests-requires-docker)
  - [Coverage Report](#coverage-report)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
  - [Code Quality](#code-quality)
  - [Project Structure](#project-structure)
- [Common Use Cases](#common-use-cases)
  - [1. Schema Evolution](#1-schema-evolution)
  - [2. Data Migrations](#2-data-migrations)
  - [3. Performance Optimizations](#3-performance-optimizations)
  - [4. Complex Refactoring](#4-complex-refactoring)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
  - [Connection Issues](#connection-issues)
  - [Migration Conflicts](#migration-conflicts)
  - [Failed Migrations](#failed-migrations)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **DAG-based migrations**: Define complex dependencies between migrations
- **Parallel execution**: Run independent migrations concurrently for faster deployments
- **Conflict detection**: Automatically detect and prevent conflicting migrations
- **Priority levels**: Control migration execution order with priorities
- **Tag system**: Organize migrations with tags for selective execution
- **Rollback support**: Safe downgrade capabilities with transaction management
- **Rich CLI**: Interactive command-line interface with colored output
- **Dry-run mode**: Preview changes before applying them

## Installation

### Using uv (recommended)

```bash
uv add morpheus-neo4j
```

### Using pip

```bash
pip install morpheus-neo4j
```

### From source

```bash
git clone https://github.com/AZX-PBC/morpheus
cd morpheus
uv sync
```

## Quick Start

### 1. Initialize Migration System

```bash
morpheus init
```

This creates:
- `migrations/` directory (or custom directory you specify)
- `migrations/versions/` directory for versioned migrations  
- `migrations/morpheus-config.yml` configuration file with default settings

### 2. Configure Database Connection

Edit `migrations/morpheus-config.yml`:

```yaml
database:
  uri: bolt://localhost:7687
  username: neo4j
  password: your-password
  database: neo4j  # optional, for multi-database setups

migrations:
  directory: ./migrations/versions

execution:
  parallel: true
  max_parallel: 4
```

#### Environment Variable Support

Morpheus supports environment variables in configuration files using OmegaConf's `${oc.env:VAR_NAME,default}` syntax:

```yaml
database:
  uri: ${oc.env:NEO4J_URI,bolt://localhost:7687}
  username: ${oc.env:NEO4J_USERNAME,neo4j}
  password: ${oc.env:NEO4J_PASSWORD,password}
  # database: ${oc.env:NEO4J_DATABASE}  # Optional database name

migrations:
  directory: ./migrations/versions

execution:
  parallel: true
  max_parallel: ${oc.env:MAX_PARALLEL,4}
```

**How it works:**
- Environment variables use `${oc.env:VAR_NAME,default}` syntax (OmegaConf resolver)
- Default values are specified after the comma
- If the environment variable isn't set, the default value will be used
- Variables without defaults will be empty if not set

**Example usage:**
```bash
# Set environment variables to override defaults
export NEO4J_URI=bolt://production:7687
export NEO4J_USERNAME=prod_user
export NEO4J_PASSWORD=secure_password
export MAX_PARALLEL=8

# Run morpheus commands - will use env vars if set, defaults otherwise
morpheus status
morpheus upgrade
```

### 3. Create Your First Migration

```bash
morpheus create initial_schema
```

This generates a migration file like `20250819_120000_initial_schema.py`:

```python
from morpheus.models.migration import MigrationBase
from morpheus.models.priority import Priority

class Migration(MigrationBase):
    """Initial schema setup."""
    
    # Define dependencies (other migration IDs that must run first)
    dependencies = []
    
    # Define conflicting migrations (cannot run in parallel)
    conflicts = []
    
    # Add tags for organization
    tags = ["schema", "initial"]
    
    # Set priority (CRITICAL, HIGH, NORMAL, LOW)
    priority = Priority.NORMAL
    
    def upgrade(self, tx):
        """Apply migration."""
        # Create constraints
        tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")
        
        # Create indexes
        tx.run("CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.created_at)")
        
    def downgrade(self, tx):
        """Rollback migration."""
        tx.run("DROP CONSTRAINT IF EXISTS ON (u:User) ASSERT u.id IS UNIQUE")
        tx.run("DROP CONSTRAINT IF EXISTS ON (u:User) ASSERT u.email IS UNIQUE")
        tx.run("DROP INDEX IF EXISTS FOR (u:User) ON (u.created_at)")
```

### 4. Apply Migrations

```bash
# Preview execution plan
morpheus upgrade --dry-run

# Apply all pending migrations
morpheus upgrade

# Apply up to a specific migration
morpheus upgrade --target 20250819_120000_initial_schema
```

## CLI Commands

### `morpheus init`

Initialize the migration system in your project. Interactive by default.

```bash
morpheus init [OPTIONS]

Options:
  --directory, -d TEXT    Migrations directory (optional)
  --non-interactive      Skip interactive prompts and use defaults
```

The init command will:
- Prompt for the migrations directory (defaults to `./migrations`)
- Create the directory structure
- Generate a config file with environment variable support
- Display next steps

### `morpheus create`

Create a new migration file.

```bash
morpheus create <name> [OPTIONS]

Options:
  --depends-on TEXT     Migration IDs this depends on (can be used multiple times)
  --conflicts-with TEXT Migration IDs that conflict (can be used multiple times)
  --tags TEXT          Tags for this migration (can be used multiple times)
  --priority TEXT      Priority level (critical/high/normal/low)
```

Examples:

```bash
# Simple migration
morpheus create add_user_properties

# With dependencies
morpheus create add_relationships --depends-on 20250819_120000_initial_schema

# With multiple options
morpheus create complex_migration \
  --depends-on migration1 \
  --depends-on migration2 \
  --conflicts-with migration3 \
  --tags performance \
  --tags optimization \
  --priority high

# With multiple dependencies and tags
morpheus create my_migration --depends-on dep1 --depends-on dep2 --tags tag1
```

### `morpheus status`

View migration status and pending migrations.

```bash
morpheus status [--format ascii|table]
```

Output shows:
- Applied migrations with execution timestamps
- Pending migrations ready to run
- Blocked migrations waiting for dependencies

### `morpheus upgrade`

Apply pending migrations to the database.

```bash
morpheus upgrade [OPTIONS]

Options:
  --target TEXT              Target migration ID to upgrade to
  --parallel/--no-parallel   Enable/disable parallel execution
  --dry-run                  Show execution plan without applying
  --ci                       Enable CI mode with detailed exit status messages
  --yes, -y                  Skip confirmation prompt
  --failfast/--no-failfast   Stop execution when any migration fails (default: False)
```

### `morpheus downgrade`

Rollback applied migrations.

```bash
morpheus downgrade [OPTIONS]

Options:
  --target TEXT        Target migration ID to downgrade to
  --branch             Smart rollback affecting only specific branch
  --dry-run           Show rollback plan without applying
```

### `morpheus dag`

Visualize and analyze the migration dependency graph.

```bash
morpheus dag [OPTIONS]

Options:
  --format TEXT        Output format (ascii/dot/json) (default: ascii)
  --output, -o PATH    Output file (default: stdout)
  --show-branches      Show independent branches
  --filter-status TEXT Filter by migration status (pending/applied/failed/rolled_back)
```

## Advanced Features

### Dependency Management

Morpheus uses a DAG (Directed Acyclic Graph) to manage migration dependencies:

```python
class Migration(MigrationBase):
    # This migration requires user and product schemas to exist first
    dependencies = [
        "20250819_120000_create_users",
        "20250819_120100_create_products"
    ]
    
    def upgrade(self, tx):
        # Can safely reference User and Product nodes
        tx.run("""
            CREATE CONSTRAINT IF NOT EXISTS 
            FOR (p:Purchase) REQUIRE p.id IS UNIQUE
        """)
        tx.run("""
            CREATE INDEX IF NOT EXISTS 
            FOR ()-[r:PURCHASED]->() ON (r.timestamp)
        """)
```

### Conflict Detection

Prevent migrations that modify the same schema elements from running in parallel:

```python
class Migration(MigrationBase):
    # Cannot run in parallel with user schema modifications
    conflicts = ["20250819_130000_modify_user_schema"]
    
    def upgrade(self, tx):
        tx.run("ALTER CONSTRAINT ON (u:User) ASSERT u.email IS UNIQUE")
```

### Priority Levels

Control execution order when migrations have the same dependency level:

```python
from morpheus.models.priority import Priority

class Migration(MigrationBase):
    priority = Priority.CRITICAL  # Runs first
    
    def upgrade(self, tx):
        # Critical system migration
        pass
```

Priority levels (highest to lowest):
- `CRITICAL`: System-critical migrations
- `HIGH`: Important schema changes
- `NORMAL`: Standard migrations (default)
- `LOW`: Non-critical optimizations

### Tag System

Organize and filter migrations with tags:

```python
class Migration(MigrationBase):
    tags = ["schema", "user", "auth"]
    
    def upgrade(self, tx):
        # User authentication related changes
        pass
```

Future: Run migrations by tag:
```bash
morpheus upgrade --tag schema
morpheus upgrade --exclude-tag experimental
```

### Parallel Execution

Morpheus automatically detects independent migrations and runs them in parallel:

```
Execution Plan:
  Batch 1: 20250819_120000_users
  Batch 2 (parallel):
    • 20250819_130000_user_properties
    • 20250819_130001_user_indexes
    • 20250819_130002_user_constraints
  Batch 3: 20250819_140000_user_relationships
```

Control parallel execution:

```bash
# Disable parallel execution
morpheus upgrade --no-parallel

# Configure max parallel migrations
# In morpheus-config.yml:
execution:
  parallel: true
  max_parallel: 4
```

## Testing

### Unit Tests

```bash
uv run pytest tests/unit -v
```

### Integration Tests (requires Docker)

```bash
# Start Neo4j container
docker run -d \
  --name neo4j-test \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/test_password \
  neo4j:latest

# Run integration tests
uv run pytest tests/integration -v
```

### Coverage Report

```bash
uv run pytest --cov=morpheus --cov-report=html
open htmlcov/index.html
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/AZX-PBC/morpheus
cd morpheus

# Install dependencies with dev extras
uv sync --dev

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check --fix

# Type checking
uv run pyright
```

### Project Structure

```
morpheus/
├── morpheus/
│   ├── cli/              # CLI commands and interface
│   │   ├── commands/     # Individual command implementations
│   │   └── utils.py      # CLI utilities
│   ├── config/           # Configuration management
│   ├── core/             # Core migration logic
│   │   ├── dag_resolver.py    # DAG resolution and validation
│   │   └── executor.py        # Migration execution engine
│   ├── models/           # Data models
│   │   ├── migration.py       # Migration base class
│   │   └── priority.py        # Priority enum
│   └── templates/        # Migration file templates
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── migrations/          # Example migrations
└── pyproject.toml       # Project configuration
```

## Common Use Cases

### 1. Schema Evolution

```python
# Migration 1: Create initial schema
class Migration(MigrationBase):
    def upgrade(self, tx):
        tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE")

# Migration 2: Add properties
class Migration(MigrationBase):
    dependencies = ["20250819_120000_initial_schema"]
    
    def upgrade(self, tx):
        tx.run("MATCH (u:User) WHERE u.created_at IS NULL SET u.created_at = datetime()")
        tx.run("CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.created_at)")
```

### 2. Data Migrations

```python
class Migration(MigrationBase):
    tags = ["data", "cleanup"]
    
    def upgrade(self, tx):
        # Migrate legacy data format
        tx.run("""
            MATCH (u:User)
            WHERE u.fullName IS NOT NULL AND u.firstName IS NULL
            SET u.firstName = split(u.fullName, ' ')[0],
                u.lastName = split(u.fullName, ' ')[1]
        """)
        
    def downgrade(self, tx):
        # Restore original format
        tx.run("""
            MATCH (u:User)
            WHERE u.firstName IS NOT NULL
            SET u.fullName = u.firstName + ' ' + u.lastName
            REMOVE u.firstName, u.lastName
        """)
```

### 3. Performance Optimizations

```python
class Migration(MigrationBase):
    priority = Priority.LOW
    tags = ["performance", "index"]
    
    def upgrade(self, tx):
        # Add composite index for query optimization
        tx.run("""
            CREATE INDEX IF NOT EXISTS FOR (u:User) 
            ON (u.country, u.city, u.created_at)
        """)
        
        # Add relationship index
        tx.run("""
            CREATE INDEX IF NOT EXISTS FOR ()-[r:FOLLOWS]->() 
            ON (r.created_at)
        """)
```

### 4. Complex Refactoring

```python
class Migration(MigrationBase):
    dependencies = ["20250819_120000_initial_schema"]
    conflicts = ["20250819_130000_other_refactor"]  # Prevent parallel execution
    
    def upgrade(self, tx):
        # Step 1: Create new structure
        tx.run("""
            MATCH (u:User)-[:POSTED]->(p:Post)
            CREATE (u)-[:AUTHORED {created_at: p.created_at}]->(p)
        """)
        
        # Step 2: Migrate data
        tx.run("""
            MATCH ()-[r:POSTED]->()
            DELETE r
        """)
        
    def downgrade(self, tx):
        # Restore original structure
        tx.run("""
            MATCH (u:User)-[r:AUTHORED]->(p:Post)
            CREATE (u)-[:POSTED]->(p)
            DELETE r
        """)
```

## Best Practices

1. **Always provide rollback logic**: Implement both `upgrade` and `downgrade` methods
2. **Use transactions**: All operations run in transactions automatically
3. **Make migrations idempotent**: Use `IF NOT EXISTS` and `IF EXISTS` clauses
4. **Keep migrations focused**: One logical change per migration
5. **Test migrations**: Always test in development before production
6. **Document dependencies**: Clearly specify migration dependencies
7. **Use meaningful names**: Migration names should describe what they do
8. **Version control**: Commit migration files to version control

## Troubleshooting

### Connection Issues

```bash
# Test connection
morpheus status

# Check Neo4j is running
docker ps | grep neo4j

# Verify credentials in morpheus-config.yml
```

### Migration Conflicts

```bash
# Check for conflicts
morpheus dag --show-branches

# Conflicts are automatically detected during upgrade
morpheus upgrade --dry-run
```

### Failed Migrations

```bash
# Check migration status
morpheus status

# Rollback last migration
morpheus downgrade --steps 1

# Fix and retry
morpheus upgrade
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Documentation: [https://morpheus-docs.example.com](https://morpheus-docs.example.com)
- Issues: [GitHub Issues](https://github.com/AZX-PBC/morpheus/issues)
- Discussions: [GitHub Discussions](https://github.com/AZX-PBC/morpheus/discussions)
