import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_messages(chat_id) -> tuple[str, bool]:
    cur = get_db().cursor()
    
    sql = f"SELECT message, fromUser FROM messages WHERE chatId = ?"
    cur.execute(sql, chat_id)
    messages = cur.fetchall()
    return messages