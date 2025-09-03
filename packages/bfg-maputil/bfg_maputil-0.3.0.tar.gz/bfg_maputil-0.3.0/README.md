# maputil

A powerful map function that improves on Python's built-in map function by adding caching and support for both lists and pandas Series.

## Features

- Caches results in a SQLite database to avoid recomputing values if the code fails or reruns
- Works with both Python lists and pandas Series
- Preserves Series indexes in the output, making it easy to add results as a new column in a DataFrame
- Supports concurrent execution with multiple threads
- Optional progress bar

## Example

```python
from maputil import map

# With a pandas Series
inputs = pd.Series([1, 2, 3, 4, 5], index=["a", "b", "c", "d", "e"])

def f(x):
    return x * 2

outputs = map(f, inputs, run="demo")
```

## Usage

The `map()` function requires a `run` parameter to identify cached results. For the same run name, the function will use cached results for inputs it has seen before.

### Optional parameters:

- `concurrency`: Number of threads to use for parallel execution
- `progress`: Set to `True` to display a progress bar
