# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2024-09-02

### Changed
- Testing GitHub Actions automated publishing workflow

## [0.1.0] - 2024-09-02

### Added
- Initial release of SimpleSpec
- Convert Python typing annotations, Pydantic v2 models, and dataclasses into human-readable schema
- Support for complex type resolution (Union, Optional, Generic types)
- Constraint and description preservation from Pydantic Field annotations
- Dataclass support with proper field handling
- Depth control for recursive structures
- Deterministic naming with collision handling
- Comprehensive test suite
- Full type hints and mypy compatibility
- Modern Python packaging with pyproject.toml
- CI/CD with GitHub Actions
- Pre-commit hooks for code quality

### Features
- `generate_simple_spec()` function as main entry point
- Support for Pydantic BaseModel and dataclasses
- Handling of forward references and recursive types
- Enum and Literal type support
- Complex container types (dict, list, tuple, set)
- Constraint extraction from annotated-types metadata
- Configurable depth limits to prevent infinite recursion

### Developer Experience
- uv for fast dependency management
- Ruff for linting and formatting
- mypy for type checking
- pytest with coverage reporting
- Pre-commit hooks
- Comprehensive documentation with examples
