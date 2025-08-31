# dnpy

A Python library for reading ~~and writing (TODO)~~ .NET assemblies.

dnpy is released under the MIT license.

## Installation

```bash
pip install dnpy
```

## Basic Usage

```python
from dnpy import Module

# Load a .NET assembly
module = Module.from_path("MyAssembly.exe")

# Iterate through types
for module_type in module.types:
    print(f"Type: {module_type.full_name}")
    
    # Check methods
    for method in module_type.methods:
        print(f"  Method: {method.name}")
        # Iterate through instructions
        for instruction in method.instructions:
            print(instruction)
```

For more examples, you can look in the `examples` folder.

## Documentation

Documentation is being prepared. When ready, it will be available in the `docs` folder along with more Guides and API References.

