# Bear Utils Configuration Module

A comprehensive configuration management system providing layered TOML configuration loading, persistent key-value settings, directory management, and specialized Pydantic models for handling paths and sensitive tokens.

## Overview

The configuration module provides three main components:

- **ConfigManager**: Environment-aware TOML configuration with Pydantic models
- **SettingsManager**: Persistent key-value settings with TinyDB backend  
- **DirectoryManager**: Standardized application directory management
- **Specialized Models**: PathModel and TokenModel for secure configuration handling

## Quick Start

### Basic Configuration Management

```python
from bear_dereth.config import ConfigManager
from pydantic import BaseModel

class AppConfig(BaseModel):
    debug: bool = False
    host: str = "localhost"  
    port: int = 8000

# Create config manager
config_manager = ConfigManager[AppConfig](
    config_model=AppConfig,
    program_name="myapp", 
    env="dev"
)

# Access configuration
config = config_manager.config
print(f"Running on {config.host}:{config.port}")
print(f"Debug mode: {config.debug}")
```

### Environment-Based Configuration

The `ConfigManager` loads configuration files in this precedence order:

1. `default.toml` - Base configuration
2. `{env}.toml` - Environment-specific (e.g., `dev.toml`, `prod.toml`)
3. `local.toml` - Local overrides (git-ignored)
4. Environment variables - Runtime overrides (prefixed with `PROGRAM_NAME_`)

**Search paths:**
- `~/.config/{program_name}/` - User configuration
- `./config/` - Project configuration (when running from project directory)

## Configuration Files

### TOML Structure

```toml
# default.toml
debug = false
host = "localhost"
port = 8000

[database]
host = "localhost"
port = 5432
name = "myapp"

[logging]
level = "INFO"
file = null
```

### Nested Configuration Models

```python
from pydantic import BaseModel
from bear_dereth.config import ConfigManager, PathModel, TokenModel

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    token: TokenModel = TokenModel()  # Secure token handling

class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: PathModel = PathModel()  # Path handling with None support

class AppConfig(BaseModel):
    debug: bool = False
    host: str = "localhost"
    port: int = 8000
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()
    
    @property
    def database_url(self) -> str:
        """Computed configuration property."""
        return f"postgresql://{self.database.host}:{self.database.port}/{self.database.name}"

# Usage
config_manager = ConfigManager[AppConfig](
    config_model=AppConfig,
    program_name="myapp",
    env="prod"
)
config = config_manager.config
print(config.database_url)
```

## Production Example

Here's a real-world configuration setup:

```python
from pydantic import BaseModel
from bear_dereth.config import ConfigManager

class Environment(BaseModel):
    name: str = "test"
    debug: bool = False
    
    @property
    def is_prod(self) -> bool:
        return self.name == "prod"
    
    @property
    def is_dev(self) -> bool:
        return self.name == "dev"

class Database(BaseModel):
    scheme: str = "sqlite:///"
    path: str = ""
    filename: str = "app.db"
    
    @property
    def url(self) -> str:
        return f"{self.scheme}{self.path}{self.filename}"

class FastAPIConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    
    @property
    def server_config(self) -> dict[str, str | int | bool]:
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "workers": self.workers,
        }

class AppConfig(BaseModel):
    database: Database = Database()
    environment: Environment = Environment()
    fastapi: FastAPIConfig = FastAPIConfig()

def get_config_manager(env: str = "prod") -> ConfigManager[AppConfig]:
    return ConfigManager[AppConfig](
        config_model=AppConfig, 
        program_name="myapp", 
        env=env
    )

# Usage
config_manager = get_config_manager("dev")
config = config_manager.config

if config.environment.is_dev:
    print("Running in development mode")

# Start FastAPI with config
import uvicorn
uvicorn.run("app:app", **config.fastapi.server_config)
```

## Environment Variables

Environment variables override TOML configuration using the pattern: `{PROGRAM_NAME}_{FIELD_NAME}={value}`

```bash
# Override host and port
export MYAPP_HOST="0.0.0.0"
export MYAPP_PORT="3000"

# Override nested values
export MYAPP_DATABASE_HOST="postgres.example.com"
export MYAPP_DATABASE_PORT="5432"
```

The ConfigManager automatically converts string environment variables to the appropriate types (int, bool, float, etc.).

## ConfigManager API

### Core Methods

```python
config_manager = ConfigManager[AppConfig](
    config_model=AppConfig,
    program_name="myapp",
    env="dev",
    config_paths=None  # Optional: custom config directories
)

# Access parsed configuration
config = config_manager.config

# Generate default configuration file
config_manager.generate_default_config()

# Check for nested configuration types
if config_manager.has_config(DatabaseConfig):
    db_config = config_manager.get_config(DatabaseConfig)
```

### Specialized Models

#### PathModel - Secure Path Handling

```python
from bear_dereth.config import PathModel

class Config(BaseModel):
    log_file: PathModel = PathModel()
    data_dir: PathModel = PathModel()

# In TOML:
# log_file = "/var/log/app.log"  -> Path object
# data_dir = null               -> None
# data_dir = ""                 -> None
```

#### TokenModel - Secure Token Storage  

```python
from bear_dereth.config import TokenModel

class Config(BaseModel):
    api_key: TokenModel = TokenModel()
    secret: TokenModel = TokenModel()

# In generated config files:
# api_key = "****"    # Hides actual values
# secret = null       # Shows unset tokens
```

## SettingsManager

Persistent key-value storage using TinyDB with automatic file change detection.

```python
from bear_dereth.config import SettingsManager, get_settings_manager

# Create settings manager
settings = SettingsManager("myapp")

# Store values
settings.user_id = "12345"
settings.set("theme", "dark")

# Retrieve values  
user_id = settings.user_id
theme = settings.get("theme", "light")

# Check existence
if "api_token" in settings:
    print("Token configured")

# Context manager usage
with SettingsManager("myapp") as settings:
    settings.window_size = (1920, 1080)

# Singleton access
settings = get_settings_manager("myapp")
```

### SettingsManager Features

- **Dot notation access**: `settings.key = value`
- **Automatic file change detection** with hash-based cache invalidation
- **In-memory caching** for performance
- **JSON persistence** with TinyDB
- **Context manager support**
- **Singleton factory** function

## DirectoryManager

Standardized application directory management following XDG conventions.

```python
from bear_dereth.config import DirectoryManager, get_config_path

# Create directory manager
dirs = DirectoryManager("myapp")

# Get standard directories
config_dir = dirs.config(mkdir=True)         # ~/.config/myapp/
local_config = dirs.local_config(mkdir=True) # ./config/myapp/ 
settings_dir = dirs.settings(mkdir=True)     # ~/.config/myapp/settings/
cache_dir = dirs.cache_path(mkdir=True)      # ~/.cache/myapp/
temp_dir = dirs.temp_path(mkdir=True)        # /tmp/myapp/

# Utility functions
config_path = get_config_path("myapp", mkdir=True)
```

### Directory Structure

```
~/.config/myapp/           # Main config directory
├── default.toml           # Default configuration
├── dev.toml              # Development config  
├── prod.toml             # Production config
├── local.toml            # Local overrides (git-ignored)
└── settings/             # Persistent settings
    └── app_settings.json
    
~/.cache/myapp/           # Cache directory
/tmp/myapp/               # Temporary files

./config/                 # Project config (when running from project dir)
└── myapp/
    ├── default.toml
    ├── dev.toml
    └── local.toml
```

## Advanced Features

### Custom Configuration Paths

```python
from pathlib import Path

config_manager = ConfigManager[AppConfig](
    config_model=AppConfig,
    program_name="myapp",
    env="prod",
    config_paths=[
        Path("/etc/myapp"),
        Path("./custom_config"),
        Path.home() / ".myapp"
    ]
)
```

### Configuration Validation

```python
from pydantic import BaseModel, field_validator

class AppConfig(BaseModel):
    port: int = 8000
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v
```

### Null Value Handling

The configuration system provides special handling for null/empty values:

```python
from bear_dereth.config import nullable_string_validator

class Config(BaseModel):
    database_url: str | None = None
    
    # Convert "null", "none", "" strings to None
    _validate_database_url = nullable_string_validator("database_url")
```

## Best Practices

1. **Use frozen models** for configuration immutability:
   ```python
   class Config(BaseModel):
       model_config = {"frozen": True}
   ```

2. **Provide sensible defaults** in your model definitions

3. **Use environment-specific configs** for different deployment environments

4. **Keep sensitive data** in environment variables or use `TokenModel`

5. **Use computed properties** for derived configuration values

6. **Keep `local.toml`** in `.gitignore` for local development overrides

## Integration Examples

### FastAPI Integration

```python
import uvicorn
from fastapi import FastAPI
from bear_dereth.config import ConfigManager

config_manager = get_config_manager()
config = config_manager.config

app = FastAPI(
    title=config.fastapi.title,
    description=config.fastapi.description,
    version=config.fastapi.version,
)

if __name__ == "__main__":
    uvicorn.run("main:app", **config.fastapi.server_config)
```

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine
from bear_dereth.config import ConfigManager

config = get_config_manager().config
engine = create_engine(config.database.url)
```

The Bear Utils configuration module provides a robust, type-safe foundation for managing application configuration across different environments and deployment scenarios.