import sqlite3
import uuid

from .db_util import get_last_run, get_run_size, new_run


def newid():
    return uuid.uuid4().hex


def get_runid(db, resume, size):
    assert isinstance(db, sqlite3.Connection)
    assert isinstance(resume, bool) or isinstance(resume, str)
    assert isinstance(size, int)

    """
    if resume is true, try to find the last run.
    if resume is a string, try to find the run with that name.
    the previous run must match the given size.
    otherwise create a new run.
    """

    if resume is True:
        last_run = get_last_run(db)
        if last_run is not None:
            last_runid, last_size = last_run
            assert last_size == size, f"size mismatch: {last_size} != {size}"
            return last_runid

    if isinstance(resume, str):
        last_size = get_run_size(db, resume)
        if last_size is not None:
            assert last_size == size, f"size mismatch: {last_size} != {size}"
            return resume

        # use the given runid
        runid = resume
    else:
        runid = newid()

    # create a new run
    new_run(db, runid, size)
    return runid
