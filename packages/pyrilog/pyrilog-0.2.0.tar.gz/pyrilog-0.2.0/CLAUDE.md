# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pyrilog is a Python-based SystemVerilog code generator that uses context managers to create hierarchical hardware descriptions. The core architecture revolves around a stack-based block system where nested `with` statements automatically manage parent-child relationships between Verilog constructs.

## Architecture

### Core Block System
The foundation is `BaseBlock` with a class-level `_current_instance_stack` that tracks the current context hierarchy. All Verilog constructs inherit from this:

- `ModuleBlock` - Verilog modules with parameters, inputs, outputs, inouts
- `AlwaysFFBlock` - SystemVerilog `always_ff` for sequential logic
- `AlwaysCombBlock` - SystemVerilog `always_comb` for combinational logic  
- `IfBlock`/`ElseBlock` - Conditional statements
- `VerilogGenerator` - Top-level container for multiple modules

### API Design Philosophy
The package exports only short aliases (prefixed with `v_`) for concise code:
- Block classes: `v_module`, `v_ff`, `v_comb`, `v_if`, `v_else`, `v_gen`
- Functions: `v_input`, `v_output`, `v_wire`, `v_reg`, `v_body`, `v_assign`, etc.

Internally, functions have descriptive names (`add_input`, `add_output`) with short aliases pointing to them.

### Port Type System
Port functions accept string `var_type` parameters instead of enums:
- `v_input("clk")` - default (no type)
- `v_input("data", 8, None, "wire")` - explicit wire type
- `v_output("out", 8, None, "reg")` - explicit reg type

Valid types: `""`, `"wire"`, `"reg"`

### Dimension Handling
The `_format_dimensions(width, dimensions)` function handles bit widths and array dimensions:
- Width comes first: `[7:0] signal_name`
- Array dimensions follow: `signal_name[9:0][3:0]`
- Single dimensions can be passed as int or in a list
- Multi-dimensional arrays require a list: `[4, 4]`

## Common Commands

### Testing
```bash
python test_pyrilog.py        # Run all tests, outputs to rtl/ folder
pytest tests/                 # Run formal test suite
```

### Development
```bash
pip install -e .              # Install in development mode
pip install -e .[test]        # Install with test dependencies
```

### Building
```bash
python -m build              # Build wheel and source distribution
```

## Generated Output Structure
- Test outputs go to `rtl/` directory (auto-created)
- SystemVerilog format with modern syntax (`always_ff`, `always_comb`)
- Dimension format: `[width] name[array_dims]`
- Integer dimensions calculated directly: `[7:0]` not `[8-1:0]`

## Key Implementation Details

### Context Stack Management
The `_find_father()` function returns the current parent block from the stack. All `v_*` functions use this to add content to the appropriate parent.

### Backward Compatibility
Long function names (`add_input`, `add_output`) still exist internally but are not exported. Only short aliases are publicly available.

### Error Handling
Port functions validate `var_type` strings and raise `ValueError` for invalid types.