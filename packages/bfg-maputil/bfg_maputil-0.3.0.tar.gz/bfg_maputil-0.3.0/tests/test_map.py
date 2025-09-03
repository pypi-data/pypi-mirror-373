import time
import uuid

import pandas as pd

from maputil import clear, select


def fast(x):
    if x is None:
        return None
    return x * 2


def slow(x):
    time.sleep(1)
    return x * 2


def test_init():
    print("clearing db")
    clear()


def test_list():
    inputs = [1, 2, 3, 4, 5]
    outputs = [2, 4, 6, 8, 10]
    assert select(fast, inputs) == outputs


def test_series():
    index = ["a", "b", "c", "d", "e"]
    inputs = pd.Series([1, 2, 3, 4, 5], index=index)
    outputs = pd.Series([2, 4, 6, 8, 10], index=index)

    results = select(fast, inputs)
    assert isinstance(results, pd.Series)
    assert results.equals(outputs)


def test_dataframe():
    index = ["a", "b", "c", "d", "e"]
    data = {"col1": [1, 2, 3, 4, 5], "col2": [10, 20, 30, 40, 50]}
    inputs = pd.DataFrame(data, index=index)

    outputs = pd.Series([2, 4, 6, 8, 10], index=index)

    results = select(lambda x: x["col1"] * 2, inputs)
    assert isinstance(results, pd.Series)
    assert results.equals(outputs)


def test_list_concurrency():
    inputs = [1, 2, 3, 4, 5]
    outputs = [2, 4, 6, 8, 10]
    assert select(slow, inputs, concurrency=3) == outputs


def test_series_concurrency():
    index = ["a", "b", "c", "d", "e"]
    inputs = pd.Series([1, 2, 3, 4, 5], index=index)
    outputs = pd.Series([2, 4, 6, 8, 10], index=index)

    results = select(slow, inputs, concurrency=3)
    assert isinstance(results, pd.Series)
    assert results.equals(outputs)


def test_null_value():
    inputs = [1, 2, None]
    outputs = [2, 4, None]
    assert select(fast, inputs) == outputs


def test_cache():
    called = 0
    inputs = [1, 2, 3, 4, 5]

    def f(x):
        nonlocal called
        called += 1
        return x * 2

    run1 = uuid.uuid4().hex
    run2 = uuid.uuid4().hex

    select(f, inputs, resume=run1)
    assert called == 5

    select(f, inputs, resume=run1)
    assert called == 5

    select(f, inputs, resume=run2)
    assert called == 10
