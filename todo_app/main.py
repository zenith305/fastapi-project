import os
import sqlite3
from contextlib import closing, asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB = Path(os.getenv('DATA_DIR', 'data')) / 'todo.db'


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


@asynccontextmanager
async def lifespan(app):
    DB.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect()) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, completed INTEGER NOT NULL DEFAULT 0)')
    yield


app = FastAPI(title='ToDo Service', lifespan=lifespan)


class Item(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    completed: bool = False


class ItemOut(Item):
    id: int


def get_item(db, item_id):
    row = db.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, 'Task not found')
    return dict(row)


@app.post('/items', response_model=ItemOut, status_code=201)
def create_item(item: Item):
    with closing(connect()) as db, db:
        cursor = db.execute('INSERT INTO items (title, description, completed) VALUES (?, ?, ?)', (item.title, item.description, item.completed))
        return get_item(db, cursor.lastrowid)


@app.get('/items', response_model=list[ItemOut])
def list_items():
    with closing(connect()) as db:
        return [dict(row) for row in db.execute('SELECT * FROM items ORDER BY id')]


@app.get('/items/{item_id}', response_model=ItemOut)
def read_item(item_id: int):
    with closing(connect()) as db:
        return get_item(db, item_id)


@app.put('/items/{item_id}', response_model=ItemOut)
def update_item(item_id: int, item: Item):
    with closing(connect()) as db, db:
        get_item(db, item_id)
        db.execute('UPDATE items SET title=?, description=?, completed=? WHERE id=?', (item.title, item.description, item.completed, item_id))
        return get_item(db, item_id)


@app.delete('/items/{item_id}', status_code=204)
def delete_item(item_id: int):
    with closing(connect()) as db, db:
        get_item(db, item_id)
        db.execute('DELETE FROM items WHERE id=?', (item_id,))
