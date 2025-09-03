import os
import sqlite3

DBFILE = "/tmp/maputil.db"

SCHEMA = """
create table if not exists item(key text primary key, val text);
create table if not exists run(name text primary key, size integer, created_at timestamp default current_timestamp);
"""


def conn():
    create_tables = False
    if not os.path.exists(DBFILE):
        create_tables = True

    db = sqlite3.connect(DBFILE, check_same_thread=False)
    if create_tables:
        db.executescript(SCHEMA)
        db.commit()
    return db


def clear():
    try:
        os.remove(DBFILE)
    except FileNotFoundError:
        pass


def set_item(db, key, val):
    assert isinstance(db, sqlite3.Connection)
    assert isinstance(key, str)
    assert isinstance(val, str)

    db.execute("insert into item(key,val) values(?,?)", (key, val))
    db.commit()


def get_item(db, key):
    assert isinstance(db, sqlite3.Connection)
    assert isinstance(key, str)

    cur = db.execute("select val from item where key=?", (key,))
    row = cur.fetchone()
    if row is None:
        return None
    (val,) = row
    return val


def get_last_run(db):
    cur = db.execute("select name,size from run order by created_at desc limit 1")
    return cur.fetchone()


def get_run_size(db, name):
    cur = db.execute("select size from run where name=?", (name,))
    row = cur.fetchone()
    if row is None:
        return None
    (size,) = row
    return size


def new_run(db, name, size):
    db.execute("insert into run(name,size) values(?,?)", (name, size))
    db.commit()
