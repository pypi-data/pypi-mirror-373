### `__init__.py`

```python
from phg import VisPHG
```

## Installation

You can install the package using pip:

```bash
pip install phg
```

## Overview

# PHG - A Minimalist Programming Language for Describing Structures

PHG (Programming HyperGraph) is a minimalist programming language inspired by the structure of bacteriophages. It combines concepts from group theory to provide custom overloading of variables and operations, making it uniquely suited for describing complex node structures such as 3D scenes and 2D sprites.

## Features

- **Node Definition**: Easily define nodes and their properties.
- **Array and Sequence Support**: Utilize both arrays and sequences for managing data.
- **Control Statements**: Implement conditional and looping logic.
- **Function Definitions**: Create custom functions for reusable code.
- **Tree Structure**: Describe hierarchical data structures effectively.
- **API Integration**: Access built-in functions for mathematical operations, drawing, and data manipulation.

## Basic Syntax

### Node Definition

```phg
{	
    a { 
        p: 1, 0, 0; 
        b { p: 2, 0, 0 }
        <a, a, a>
        [a, a, a]           
    }
}
```

### Control Statements

```phg
?(condition) { statement } : { else statement };
@n { statement1 ? (_i = x) ~; statement2; }
```

### Function Definition

```phg
$functionName(args...) { statement $return }
```

## Sequences and Arrays

- **Sequence**: `<a, b, c, d>` corresponds to `{a {b {c {d}}}}`
- **Array**: `[a, b, c, d]` corresponds to `{{a}{b}{c}{d}}`

### Example

```phg
node1 { 
    pos: 1, 2, 3; 
    node2 { x: 1; node3 { y: 1 } } 
}
```

## Built-in Functions

- **Math Functions**: `rnd()`, `sin()`, `cos()`
- **Node Operations**: `im()`, `on()`, `wak()`, `dump()`
- **Data Conversion**: `tojson()`

## Installation

You can install PHG via PyPI:

```bash
pip install phg
```

## Usage

To use PHG, simply import the module in your Python project:

```python
import phg

# Define your PHG code as a string
phg_code = """
{
    a {
        p: 1, 0, 0;
        b { p: 2, 0, 0 }
    }
}
"""

# Execute the PHG code
phg.run(phg_code)
```

## Documentation

For more detailed information on syntax, functions, and examples, please refer to the [official documentation](https://your.documentation.link).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgements

PHG is inspired by concepts from group theory and aims to provide a flexible way to describe complex data structures in programming.