# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2024-08-31

### Fix
- Entity linker request timeout

## [1.1.0] - 2024-08-19

### Added
- **Batch Linking**: Batch linking solves the challenge of linking multiple entities at once
Added link_entities_batch method to efficiently processes multiple entities by first batch inserting them 
into the database, then performing parallel linking operations. The batch approach significantly 
improves performance compared to linking entities individually.


## [1.0.2] - 2024-08-19

### Changed
- Minor improvements and bug fixes
- Updated package configuration

## [1.0.0] - 2024-08-19

### Added
- Initial release of Entity Linker Client
- Core EntityLinker class with full API support
- Support for entity CRUD operations (Create, Read, Update, Delete)
- Batch entity operations for efficient processing
- Entity linking capabilities with configurable matching strategies
- Multiple matching types: strict match, lexical similarity, semantic similarity, dictionary matching
- Flexible configuration system with EntityLinkingConfig
- Static methods for linker management
- Comprehensive type annotations for better developer experience
- HTTP client with proper error handling
- Environment variable support for configuration
- Complete documentation and examples

### Features
- **Entity Management**: Add, modify, delete, and retrieve entities
- **Batch Operations**: Efficient processing of multiple entities
- **Intelligent Linking**: Multiple matching strategies for entity resolution
- **Flexible Configuration**: Customizable matching rules and thresholds  
- **Type Safety**: Full type annotations throughout the codebase
- **Error Handling**: Robust error handling for HTTP and configuration errors
- **Environment Support**: Configuration via environment variables

### API
- `EntityLinker` - Main client class
- `EntityLinkingConfig` - Configuration management
- `MatchType` - Enum for matching strategies
- `FieldCondition`, `AndCondition`, `OrCondition` - Configuration building blocks
- `DictFieldMapping` - Dictionary field mapping configuration

### Dependencies
- httpx >= 0.24.0 - HTTP client library
- python-dotenv >= 0.19.0 - Environment variable management

### Development
- Modern build system with pyproject.toml
- Comprehensive test coverage
- Development tools: pytest, black, isort, mypy, flake8
- Jupyter notebook examples and demonstrations
