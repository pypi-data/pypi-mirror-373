# Changelog

All notable changes to Skald will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-08-31

### Added

#### Core Features
- **SurveyingProxy**: Main proxy class for transparent MCP server wrapping
- **Feedback Collection**: `feedback.report` tool with structured JSON schema
- **Trace ID System**: UUID-based tracing for all tool calls
- **Metrics Collection**: Automatic latency, output size, and status tracking

#### Opt-out Controls
- **@opt_out decorator**: Function-level feedback collection suppression
- **suppressed() context manager**: Block-level feedback collection control
- **Thread-safe implementation**: Using contextvars for proper isolation

#### Storage System
- **SQLite Backend**: Default storage with proper schema and foreign keys
- **TTL Support**: Configurable data retention and cleanup
- **Data Redaction**: Sensitive information removal from stored arguments
- **Transactional Consistency**: ACID compliance for all operations

#### Transport Support
- **Standard I/O Transport**: Native MCP protocol support
- **TCP Transport**: JSON-RPC over TCP with proper connection handling
- **Unix Socket Support**: Local inter-process communication
- **Extensible Architecture**: Abstract base classes for custom transports

#### Feedback System
- **Smart Invitations**: Error-based, latency-based, and sampling-based feedback invites
- **Structured Schema**: 5-point ratings for helpfulness, fit, and clarity
- **Confidence Scoring**: 0.0-1.0 confidence levels
- **Suggestion System**: Up to 3 suggestions per feedback, max 100 chars each
- **Better Alternative Tracking**: Enum-based alternative tool suggestions

#### CLI Interface
- **Multi-protocol Server**: Support for stdio, TCP, and Unix sockets
- **Feedback Querying**: Database inspection and reporting commands
- **Data Management**: Cleanup and maintenance utilities
- **Demo Mode**: Built-in example MCP server for testing

#### Quality Assurance
- **81%+ Test Coverage**: Comprehensive unit and integration tests
- **Type Safety**: Full mypy compliance with strict mode
- **Security**: Bandit security scanning and safe data handling
- **Performance**: Minimal overhead design with async-first architecture

#### Development Infrastructure
- **GitHub Actions**: Automated CI/CD pipeline
- **Pre-commit Hooks**: Code quality enforcement
- **Multiple Python Versions**: Support for 3.9, 3.10, 3.11, 3.12
- **Cross-platform**: Linux, macOS, and Windows compatibility

### Technical Details

#### Database Schema
- `tool_runs` table: Execution metadata with proper indexing
- `tool_feedback` table: Structured feedback with foreign key constraints
- Automatic schema migration and version management
- Built-in data integrity checks

#### API Surface
- **SurveyingProxy**: Main class with comprehensive configuration options
- **Storage Backends**: Abstract interface with SQLite implementation
- **Transport Protocols**: Base classes and concrete implementations
- **Data Models**: Pydantic v2 schemas with strict validation

#### Performance Characteristics
- **Sub-millisecond Overhead**: Minimal impact on tool call latency
- **Async Background Processing**: Non-blocking feedback storage
- **Memory Efficient**: Streaming data processing for large outputs
- **Connection Pooling**: Efficient resource management

#### Security Features
- **Input Validation**: All external data validated with Pydantic
- **SQL Injection Prevention**: Parameterized queries throughout
- **Sensitive Data Redaction**: Configurable PII removal
- **Safe Error Handling**: No information leakage in error messages

### Documentation
- **Comprehensive README**: Full usage examples and configuration guide
- **API Documentation**: Google-style docstrings for all public APIs
- **Contributing Guide**: Development setup and coding standards
- **Architecture Documentation**: Design decisions and extensibility points

[Unreleased]: https://github.com/sibyllinesoft/skald/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sibyllinesoft/skald/releases/tag/v0.1.0