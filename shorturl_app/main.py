import os
import secrets
import sqlite3
from contextlib import closing, asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

DB = Path(os.getenv('DATA_DIR', 'data')) / 'links.db'


@asynccontextmanager
async def lifespan(app):
    DB.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS links (short_id TEXT PRIMARY KEY, full_url TEXT NOT NULL)')
    yield


app = FastAPI(title='Short URL Service', lifespan=lifespan)


class Link(BaseModel):
    url: HttpUrl


def find_url(short_id):
    with closing(sqlite3.connect(DB)) as db:
        row = db.execute('SELECT full_url FROM links WHERE short_id=?', (short_id,)).fetchone()
    if row is None:
        raise HTTPException(404, 'Link not found')
    return row[0]


@app.post('/shorten', status_code=201)
def shorten(link: Link, request: Request):
    with closing(sqlite3.connect(DB)) as db, db:
        while True:
            short_id = secrets.token_hex(4)
            cursor = db.execute('INSERT OR IGNORE INTO links VALUES (?, ?)', (short_id, str(link.url)))
            if cursor.rowcount:
                break
    return {'short_id': short_id, 'short_url': str(request.url_for('redirect', short_id=short_id))}


@app.get('/stats/{short_id}')
def stats(short_id: str):
    return {'short_id': short_id, 'full_url': find_url(short_id)}


@app.get('/{short_id}')
def redirect(short_id: str):
    return RedirectResponse(find_url(short_id), status_code=307)
