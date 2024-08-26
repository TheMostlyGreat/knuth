## 16. Pythonic Code Principles

### 16.1 Use Python’s Built-in Functions and Libraries
```python
# Instead of this:
squares = []
for x in range(10):
    squares.append(x**2)

# Do this:
squares = [x**2 for x in range(10)]
```

### 16.2 Use List Comprehensions and Generator Expressions
```python
# List comprehension
squares = [x**2 for x in range(10)]

# Generator expression
squares_gen = (x**2 for x in range(10))
```

### 16.3 Use Enumerate Instead of Range
```python
# Instead of this:
for i in range(len(my_list)):
    print(i, my_list[i])

# Do this:
for index, value in enumerate(my_list):
    print(index, value)
```

### 16.4 Use `with` for Resource Management
```python
# Instead of this:
file = open("file.txt", "r")
try:
    data = file.read()
finally:
    file.close()

# Do this:
with open("file.txt", "r") as file:
    data = file.read()
```

### 16.5 Handle Exceptions Properly
```python
# Instead of this:
try:
    risky_operation()
except:
    handle_error()

# Do this:
try:
    risky_operation()
except SpecificException as e:
    handle_error(e)
```

### 16.6 Use `f-strings` for String Formatting
```python
# Instead of this:
name = "Alice"
greeting = "Hello, %s!" % name

# Or this:
greeting = "Hello, {}".format(name)

# Do this:
greeting = f"Hello, {name}!"
```

### 16.7 Write Functions with Single Responsibility
- Each function should do one thing well.

### 16.8 Use `dataclasses` for Simple Classes
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

### 16.9 Prefer `is` for Comparing to `None`
```python
# Instead of this:
if value == None:
    ...

# Do this:
if value is None:
    ...
```

### 16.10 Simplify Conditions
```python
# Instead of this:
if len(my_list) > 0:
    ...

# Do this:
if my_list:
    ...
```
