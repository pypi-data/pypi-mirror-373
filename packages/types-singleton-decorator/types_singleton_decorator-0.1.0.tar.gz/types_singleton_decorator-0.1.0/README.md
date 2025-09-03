# types-singleton-decorator

Type stubs for the `singleton_decorator` package to provide proper type hints and fix Pylance type checking issues.

## Problem Solved

When using the `singleton_decorator` decorator, Pylance shows the error:
```
Expected class but received "_SingletonWrapper" PylancereportGeneralTypeIssues
```

This package provides proper type stubs to resolve this issue and ensure your IDE understands that decorated classes remain classes.

## Installation

Install using pip:
```bash
pip install types-singleton-decorator
```

Or using uv:
```bash
uv add types-singleton-decorator
```

## Usage

Once installed, the type stubs will automatically be picked up by your type checker (Pylance, mypy, etc.). No additional configuration is needed.

Your singleton decorators will now have proper type support:

```python
from singleton_decorator import singleton

@singleton
class MyClass:
    def __init__(self, value: str):
        self.value = value
    
    def get_value(self) -> str:
        return self.value

# This will now have proper type hints
instance = MyClass("hello")  # Type: MyClass, not _SingletonWrapper
print(instance.get_value())  # Pylance understands this method exists
```

## What's Included

This package provides type stubs for:
- `@singleton` decorator
- `SingletonMeta` metaclass (if used)
- Proper preservation of class types and methods

## Requirements

- Python >= 3.8
- The original `singleton_decorator` package 

## Contributing

Issues and pull requests are welcome at the [GitHub repository](https://github.com/rohitshubham/types-singleton-decorator).

## License

MIT License
