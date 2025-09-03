# ExposedFunctionality

ExposedFunctionality is a Python library designed to facilitate the interaction between backend code and frontend interfaces. It enables developers to expose backend methods and variables in a structured and secure way, making it easier to integrate with front-end systems or API endpoints. This library is particularly useful in scenarios where backend logic needs to be accessed or manipulated from a front-end application or through web API calls.

## Features

- **Function Exposition:** Expose backend functions with added metadata, such as parameter types, return types, and descriptions, making it easier for frontend applications to understand and use these functions.
- **Variable Exposition:** Expose backend variables in a controlled manner, with support for type enforcement, default values, and change events.
- **Docstring Parsing:** Automatically parse function docstrings to extract parameter and return value descriptions, further enriching the exposed method's metadata.
- **Type Safety:** Enforce type checks on exposed variables and function parameters to reduce runtime errors and ensure data integrity.
- **Event Handling:** Support for change events on exposed variables, allowing the frontend to react to changes in the backend state.
- **Middleware Integration:** Apply middleware functions to exposed variables for additional processing or validation before setting their values.
- **Dynamic Addition:** Dynamically add exposed functions and variables to instances or classes, enhancing flexibility in runtime object configuration.

## Installation

To install ExposedFunctionality, use pip:

```bash
pip install exposedfunctionality
```

## Usage

### Exposing Functions

To expose a backend function, use the `exposed_method` decorator. This allows you to specify metadata such as the method's name, input parameters, and output parameters.

```python
from exposedfunctionality import exposed_method

@exposed_method(name="calculate_sum", inputs=[{"name": "a", "type": "int"}, {"name": "b", "type": "int"}], outputs=[{"name": "result", "type": "int"}])
def add(a, b):
    """Calculate the sum of two numbers."""
    return a + b
```

To retrieve exposed methods from an object (either an instance or a class), you can use the `get_exposed_methods` function provided by the `exposedfunctionality` package. This function scans an object for methods that have been decorated with `@exposed_method` and collects them into a dictionary, making it easy to access and utilize these methods programmatically, such as when dynamically generating API endpoints or interfaces.

### Example

Consider the following class with an exposed method:

```python
from exposedfunctionality import exposed_method, get_exposed_methods

class MathOperations:
    @exposed_method(name="add", inputs=[{"name": "a", "type": "int"}, {"name": "b", "type": "int"}], outputs=[{"name": "sum", "type": "int"}])
    def add_numbers(self, a, b):
        """Add two numbers."""
        return a + b
```

To retrieve the exposed methods from an instance of `MathOperations`, you would do the following:

```python
math_operations = MathOperations()

exposed_methods = get_exposed_methods(math_operations)

for method_name, (method, metadata) in exposed_methods.items():
    print(f"Method Name: {method_name}")
    print(f"Metadata: {metadata}")
    print(f"Function: {method}")
    print("-----")
```

This will output something like:

```
Method Name: add
Metadata: {'name': 'add', 'input_params': [{'name': 'a', 'type': 'int', 'positional': True}, {'name': 'b', 'type': 'int', 'positional': True}], 'output_params': [{'name': 'sum', 'type': 'int'}], 'docstring': {'summary': 'Add two numbers.', 'original': 'Add two numbers.', 'input_params': [], 'output_params': [], 'exceptions': {}}}
Function: <bound method MathOperations.add_numbers of <__main__.MathOperations object at 0x7fcd1830f1f0>>
-----
```

The `get_exposed_methods` function is particularly useful for frameworks or libraries that need to dynamically discover which methods are available for external access, such as in web frameworks for automatically generating API routes or in GUI applications for dynamically creating user interface elements based on the backend logic.

### Exposing Variables

Expose backend variables using the `ExposedValue` descriptor. This enables type checking, default values, and change event handling.

```python
from exposedfunctionality.variables import ExposedValue

class Calculator:
    result = ExposedValue("result", default=0, type_=int)

calculator = Calculator()
calculator.result = 5  # Sets the result and enforces type checking
```

### Listening to Variable Changes

You can listen to changes on an exposed variable by attaching an `OnChangeEvent`:

```python
def on_result_change(new_value, old_value):
    print(f"Result changed from {old_value} to {new_value}")

calculator.result.add_on_change_callback(on_result_change)
calculator.result = 10  # Triggers the on_result_change callback
```

### Applying Middleware

Use middleware functions to process or validate variable values before they are set:

```python
from exposedfunctionality.variables.middleware import min_max_clamp

class RestrictedCalculator:
    result = ExposedValue("result", default=0, type_=int, valuechecker=[min_max_clamp],max=100)

restricted_calculator = RestrictedCalculator()
restricted_calculator.result = 150  # The value will be clamped to 100
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
