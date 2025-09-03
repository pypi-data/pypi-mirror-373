# SimpleSpec

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/simplespec.svg)](https://badge.fury.io/py/simplespec)

Convert Python typing annotations, Pydantic v2 models, and dataclasses into a compact, human‑readable schema specification.

## Features

- 🔍 **Clear, readable type strings** - Modern Python syntax (e.g., `list[T]`, `dict[K, V]`, `Union` via `|`)
- 📝 **Preserve constraints and descriptions** - Field descriptions and validation constraints
- 🏗️ **First-class Pydantic & dataclass support** - Referenced types with proper handling
- 🔄 **Deterministic naming** - Collision handling for types with same names
- 🛡️ **Depth control** - Configurable limits for cyclic/recursive structures
- ⚡ **Fast and lightweight** - Minimal dependencies

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv add simplespec

# Using pip
pip install simplespec
```

### Basic Usage

```python
from pydantic import BaseModel, Field
from simplespec import generate_simple_spec

class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    name: str
    age: int = Field(ge=18, description="User's age in years")
    address: Address

spec = generate_simple_spec(User)
print(spec)
```

**Output:**
```
Referenced specs:
Address
    street: str
    city: str
Spec:
User
    name: str
    age: int, User's age in years [ge=18]
    address: Address
```

## API Reference

### `generate_simple_spec`

```python
from simplespec import generate_simple_spec, DepthLimitExceededError, SimpleSpecError

spec = generate_simple_spec(root_type_obj, max_depth: int | None = None)
```

**Parameters:**
- `root_type_obj`: Any supported type (Pydantic BaseModel class, dataclass type, or typing annotations like `list[str]`, `dict[str, int]`, `Union`, etc.)
- `max_depth`: Optional recursion limit for referenced types (default: 4)

**Returns:**
- `Spec`: A dataclass containing:
  - `self`: `Ref` — The root type definition
  - `refs`: `list[Ref]` — Referenced Pydantic models/dataclasses, sorted by depth then name

**Raises:**
- `DepthLimitExceededError` — When walking exceeds max_depth
- `SimpleSpecError` — For other analysis/build failures

### Output Data Structures

```python
@dataclass
class Prop:
    type: str
    description: str | None = None

@dataclass  
class Ref:
    type: str
    description: str | None = None
    properties: dict[str, Prop] = field(default_factory=dict)

@dataclass
class Spec:
    self: Ref
    refs: list[Ref] = field(default_factory=list)
```

## Type Resolution Examples

SimpleSpec normalizes type names to modern Python syntax:

| Input Type | Output |
|------------|--------|
| `dict[str, int]` | `"dict[str, int]"` |
| `list[User \| None]` | `"list[User \| None]"` |
| `Optional[str]` | `"str \| None"` |
| `Union[str, int, None]` | `"int \| str \| None"` |
| `tuple[str, int]` | `"tuple[str, int]"` |
| `set[int]` | `"set[int]"` |
| `Literal['a', 'b']` | `"Literal['a', 'b']"` |

## Advanced Examples

### Recursive Types

```python
class TreeNode(BaseModel):
    value: str
    children: list["TreeNode"] = []
    parent: Optional["TreeNode"] = None

TreeNode.model_rebuild()  # Required for forward references

spec = generate_simple_spec(TreeNode)
print(spec.self.properties["children"].type)  # "list[TreeNode]"
```

### Dataclass Support

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float = 0.0

class Shape(BaseModel):
    center: Point
    points: list[Point]

spec = generate_simple_spec(Shape)
# Point appears in spec.refs as a referenced type
```

### Complex Constraints

```python
class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Product name")
    price: float = Field(gt=0, le=10000, description="Price in USD")
    quantity: int = Field(ge=0, multiple_of=1)

spec = generate_simple_spec(Product)
# Constraints appear as: "str, Product name [min_length=1] [max_length=100]"
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/denizkenan/simplespec.git
cd simplespec

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=simplespec --cov-report=html

# Run specific test
uv run pytest tests/test_simplespec.py::test_simple_for_primitive_type -v
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code  
uv run ruff check

# Type check
uv run mypy simplespec
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`uv run pytest`)
6. Run code quality checks (`uv run ruff check && uv run mypy simplespec`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Compatibility

- **Python**: 3.11+
- **Pydantic**: v2.0+
- **Dependencies**: `pydantic>=2.0.0`, `annotated-types>=0.6.0`

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pydantic](https://docs.pydantic.dev/) for model handling
- Uses [annotated-types](https://github.com/annotated-types/annotated-types) for constraint extraction
- Development tooling by [uv](https://docs.astral.sh/uv/) and [Ruff](https://docs.astral.sh/ruff/)
