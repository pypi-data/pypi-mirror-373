# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-12-31

### Fixed
- **Cache Directory Issue**: Fixed "Read-only file system" error when running via uvx
  - Changed default cache directories to use user cache directory instead of relative paths
  - Added platformdirs dependency for cross-platform user directory detection
  - Services now create cache directories in user-writable locations by default

## [0.2.0] - 2024-12-31

### Added
- **Comprehensive Error Handling System**
  - Custom error classes for different failure types (NetworkError, SearchError, IndexingError, etc.)
  - User-friendly error messages for MCP responses
  - Structured error logging with context and timing information
  - Error classification and conversion utilities

- **Advanced Monitoring and Health Checks**
  - Multi-level health check system (liveness, readiness, component health)
  - Health check MCP tools for monitoring server status
  - Component-level health monitoring for all services
  - Network connectivity monitoring

- **Resilience Features**
  - Circuit breaker pattern for preventing cascading failures
  - Retry logic with exponential backoff for network operations
  - Graceful degradation when components fail
  - Background error recovery mechanisms

- **Enhanced Logging**
  - Structured JSON logging with operation context
  - Performance timing for all operations
  - Error tracking and counting
  - Configurable log levels for different components

### Changed
- Improved server initialization with better error handling
- Enhanced service initialization with timeout protection
- Better error propagation through MCP tool chain
- More robust background update processes

### Fixed
- Server continues operating when individual components fail
- Better handling of network timeouts and connection failures
- Improved error messages for validation failures
- More reliable service recovery after temporary failures

## [0.1.8] - 2024-12-30

### Added
- Fast startup implementation with bundled cache system
- Cache hierarchy (user cache → bundled cache → fetch from GitHub)
- Background documentation updates
- Performance optimizations for server initialization

### Changed
- Improved caching strategy for better performance
- Enhanced documentation indexing process

### Fixed
- Various stability improvements
- Better handling of missing documentation cache

## [0.1.0] - 2024-12-29

### Added
- Initial release of Strands MCP Server
- Documentation search functionality using semantic search
- GitHub documentation fetching and caching
- FAISS-based vector search
- MCP protocol implementation with FastMCP
- Basic health monitoring
- Project setup and configuration tools