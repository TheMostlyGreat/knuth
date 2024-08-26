## Best Practices for Writing Functions

### Function Length
- Keep functions small and focused on a single task.
  - Aim for functions to be 20-30 lines of code or less.
  - If a function exceeds 50 lines, consider breaking it into smaller, more focused functions.
- Prioritize readability and maintainability over arbitrary line count limits.

### Function Arguments

- Limit the number of arguments to a maximum of 5.
  - Ideal: 0-3 arguments
  - Acceptable: 4-5 arguments
  - Avoid: More than 5 arguments
- Use descriptive parameter names to enhance readability.
- Consider using default values for optional arguments.
- For functions requiring many parameters, use a dictionary or dataclass.
- Order parameters: required, optional with default values, *args, **kwargs.
- Use type hints to specify argument types.

Examples:
```python
# Good: 3 arguments
def calculate_area(length: float, width: float, unit: str = "m²") -> str:
    return f"{length * width} {unit}"

# Acceptable: 5 arguments
def create_user(username: str, email: str, password: str, 
                first_name: str = "", last_name: str = "") -> User:
    # ...

### Avoid Side Effects
- Avoid modifying global state or arguments within functions.
- Strive for pure functions that only operate on their inputs and return a result.
- If side effects are necessary, clearly document them in the function's docstring.

#### Guidelines:
1. Don't modify global variables:
   - Instead, pass necessary data as arguments and return modified values.
2. Avoid modifying mutable arguments:
   - If modification is required, consider returning a new object instead.
3. Use return values instead of modifying arguments in-place:
   - This makes the function's behavior more predictable and easier to test.
4. Clearly name functions that have side effects:
   - Use verbs that imply modification (e.g., `update_`, `modify_`, `set_`).

#### Examples:

```python
# Bad: Modifying a global variable
total = 0

def add_to_total(value):
    global total
    total += value  # Side effect: modifies global state

# Good: Using parameters and return values
def add_numbers(a, b):
    return a + b  # Pure function, no side effects

# Bad: Modifying a mutable argument
def append_to_list(item, lst=[]):
    lst.append(item)  # Side effect: modifies the default list
    return lst

# Good: Creating and returning a new list
def append_to_list(item, lst=None):
    if lst is None:
        lst = []
    return lst + [item]  # Returns a new list, no side effects

# If side effects are unavoidable, document them clearly
def update_user_profile(user, new_data):
    """
    Update the user's profile with new data.

    Side effects:
    - Modifies the user object in-place
    - Saves changes to the database
    """
    user.update(new_data)