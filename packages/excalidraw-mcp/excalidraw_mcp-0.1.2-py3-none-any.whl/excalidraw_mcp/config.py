"""Configuration management for Excalidraw MCP server."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class SecurityConfig:
    """Security-related configuration."""

    # Authentication
    auth_enabled: bool = False  # Disabled by default for development
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    token_expiration_hours: int = 24

    # CORS
    allowed_origins: list[str] = None
    cors_credentials: bool = True
    cors_methods: list[str] = None
    cors_headers: list[str] = None

    # Rate limiting
    rate_limit_window_minutes: int = 15
    rate_limit_max_requests: int = 100

    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:3031", "http://127.0.0.1:3031"]
        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.cors_headers is None:
            self.cors_headers = ["Content-Type", "Authorization", "X-Requested-With"]


@dataclass
class ServerConfig:
    """Server configuration settings."""

    # Express server
    express_url: str = "http://localhost:3031"
    express_host: str = "localhost"
    express_port: int = 3031

    # Health checks
    health_check_timeout_seconds: float = 5.0
    health_check_interval_seconds: int = 30
    health_check_max_failures: int = 3

    # Sync operations
    sync_operation_timeout_seconds: float = 10.0
    sync_retry_attempts: int = 3
    sync_retry_delay_seconds: float = 1.0

    # Process management
    canvas_auto_start: bool = True
    startup_timeout_seconds: int = 30
    startup_retry_delay_seconds: float = 1.0
    graceful_shutdown_timeout_seconds: float = 10.0

    def __post_init__(self):
        """Validate and parse configuration."""
        parsed = urlparse(self.express_url)
        if parsed.hostname:
            self.express_host = parsed.hostname
        if parsed.port:
            self.express_port = parsed.port


@dataclass
class PerformanceConfig:
    """Performance-related configuration."""

    # Connection pooling
    http_pool_connections: int = 10
    http_pool_maxsize: int = 20
    http_keep_alive: bool = True

    # WebSocket
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    websocket_close_timeout: int = 10

    # Memory management
    max_elements_per_canvas: int = 10000
    element_cache_ttl_hours: int = 24
    memory_cleanup_interval_minutes: int = 60

    # Message batching
    websocket_batch_size: int = 50
    websocket_batch_timeout_ms: int = 100

    # Query optimization
    enable_spatial_indexing: bool = True
    query_result_limit: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str | None = None
    max_file_size_mb: int = 100
    backup_count: int = 5

    # Security logging
    audit_enabled: bool = True
    audit_file_path: str | None = None
    sensitive_fields: list[str] = None

    def __post_init__(self):
        if self.sensitive_fields is None:
            self.sensitive_fields = ["password", "token", "secret", "key"]


class Config:
    """Main configuration class."""

    def __init__(self):
        self.security = SecurityConfig()
        self.server = ServerConfig()
        self.performance = PerformanceConfig()
        self.logging = LoggingConfig()
        self._load_from_environment()
        self._validate()

    def _load_from_environment(self):
        """Load configuration from environment variables."""

        # Security config
        self.security.auth_enabled = (
            os.getenv("AUTH_ENABLED", "false").lower() == "true"
        )
        self.security.jwt_secret = os.getenv("JWT_SECRET", "")

        origins_env = os.getenv("ALLOWED_ORIGINS")
        if origins_env:
            self.security.allowed_origins = [o.strip() for o in origins_env.split(",")]

        # Server config
        self.server.express_url = os.getenv(
            "EXPRESS_SERVER_URL", self.server.express_url
        )
        self.server.canvas_auto_start = (
            os.getenv("CANVAS_AUTO_START", "true").lower() != "false"
        )

        # Performance config
        if os.getenv("MAX_ELEMENTS"):
            self.performance.max_elements_per_canvas = int(os.getenv("MAX_ELEMENTS"))

        # Logging config
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        self.logging.file_path = os.getenv("LOG_FILE")
        self.logging.audit_file_path = os.getenv("AUDIT_LOG_FILE")

    def _validate(self):
        """Validate configuration values."""
        errors = []

        # Validate security config
        if self.security.auth_enabled and not self.security.jwt_secret:
            errors.append("JWT_SECRET is required when authentication is enabled")

        if self.security.token_expiration_hours <= 0:
            errors.append("Token expiration must be positive")

        # Validate server config
        if self.server.express_port <= 0 or self.server.express_port > 65535:
            errors.append("Express port must be between 1 and 65535")

        if self.server.health_check_timeout_seconds <= 0:
            errors.append("Health check timeout must be positive")

        # Validate performance config
        if self.performance.max_elements_per_canvas <= 0:
            errors.append("Max elements per canvas must be positive")

        if self.performance.websocket_batch_size <= 0:
            errors.append("WebSocket batch size must be positive")

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Global configuration instance
config = Config()
