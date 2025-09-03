import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import pandas as pd

from .db_util import conn, get_item, set_item
from .progress import tqdm
from .run_util import get_runid


def select(
    fn: Callable,
    inputs: list | pd.Series | pd.DataFrame,
    resume: bool | str = False,
    progress: bool = False,
    concurrency: int = 1,
) -> list | pd.Series:
    """
    Apply a function to a collection of inputs with caching and optional concurrency.

    Parameters:
    -----------
    fn : callable
        The function to apply to each input element.
    inputs : list or pandas.Series or pandas.DataFrame
        The collection of input values to process.
    resume : bool or str, default=False
        If True, resume the last run. If a string, resume the run with that name.
        If False, create a new run with a random identifier.
    progress : bool, default=False
        Whether to display a progress bar during execution.
    concurrency : int, default=1
        Number of concurrent workers. If greater than 1, processing is done in parallel.

    Returns:
    --------
    list or pandas.Series
        If inputs was a list, returns a list of results.
        If inputs was a pandas.Series or pandas.DataFrame, returns a pandas.Series with the same index.

    Notes:
    ------
    Results are cached in a SQLite database based on the resume identifier and input position.
    Subsequent calls with the same resume identifier will use cached results without recomputation.
    The caching is persistent across program restarts, making it useful for long-running or failure-prone processes.
    """
    assert callable(fn)
    assert isinstance(inputs, (list, pd.Series, pd.DataFrame))
    assert isinstance(resume, (bool, str))
    assert isinstance(progress, bool)
    assert isinstance(concurrency, int) and concurrency > 0

    if isinstance(inputs, pd.Series):
        # process each item of the Series and return a Series with the same index
        outputs = maplist(fn, inputs.tolist(), resume, progress, concurrency)
        return pd.Series(outputs, index=inputs.index)
    elif isinstance(inputs, pd.DataFrame):
        # process each row of the DataFrame and return a Series with the same index
        outputs = maplist(
            fn, inputs.to_dict(orient="records"), resume, progress, concurrency
        )
        return pd.Series(outputs, index=inputs.index)
    else:
        return maplist(fn, inputs, resume, progress, concurrency)


def maplist(fn, inputs, resume, progress, concurrency):
    dblock = threading.Lock()
    size = len(inputs)
    if progress:
        pbar = tqdm(total=size)
    else:
        pbar = None

    with conn() as db:
        runid = get_runid(db, resume, size)

        if resume != runid:
            print("runid:", runid, flush=True)

        def memfn(i):
            key = f"{runid}:{i}"

            with dblock:
                # try to get cached result
                jsonval = get_item(db, key)

            if jsonval is None:
                # if not cached, compute result
                try:
                    val = fn(inputs[i])
                except Exception as e:
                    print("failed at index", i, flush=True)
                    raise e

                jsonval = json.dumps(val)
                with dblock:
                    # save result to cache
                    set_item(db, key, jsonval)
            else:
                # if cached, load result
                val = json.loads(jsonval)

            if pbar:
                pbar.update(1)
            return val

        if concurrency == 1:
            outputs = map(memfn, range(size))
        else:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                outputs = executor.map(memfn, range(size))
        outputs = list(outputs)

    if pbar:
        pbar.close()
    return outputs
