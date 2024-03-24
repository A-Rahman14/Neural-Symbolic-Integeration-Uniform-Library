# DIMACS Formatter

`DIMACSFormatter` is a Python class designed to facilitate the creation of propositional logic problems in the DIMACS format. This format is widely used in computational logic, particularly in SAT solvers. The class allows for the dynamic addition of variables and clauses and generates a string conforming to the DIMACS standard.

## Class Methods

### `__init__(self)`

Initializes a new instance of the `DIMACSFormatter` class.

- Initializes an empty set of variables and an empty list of clauses.

### `add_clause(self, clause)`

Adds a new clause to the DIMACS problem.

- **Parameters:**
    - `clause` (list of int): A list of integers representing a single clause. Positive integers denote the variable itself, while negative integers denote the negation of the variable.
- **Returns:** None.

### `generate_dimacs(self)`

Generates the DIMACS formatted string based on the added clauses and variables.

- **Returns:** 
    - `str`: A string formatted according to DIMACS standards, including the problem line and the list of clauses.

### `reset(self)`

Resets the `DIMACSFormatter` instance to its initial state, clearing all variables and clauses.

- **Returns:** None.

## Example Usage

```python
dimacs_formatter = DIMACSFormatter()

# Adding clauses to represent the formula: (x1 OR NOT x2) AND (NOT x1 OR x3)
dimacs_formatter.add_clause([1, -2])  # Represents x1 OR NOT x2
dimacs_formatter.add_clause([-1, 3])  # Represents NOT x1 OR x3

# Generating the DIMACS formatted string
dimacs_string = dimacs_formatter.generate_dimacs()
print(dimacs_string)
