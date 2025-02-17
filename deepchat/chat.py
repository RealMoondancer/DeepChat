import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from deepchat.db import get_db

from . import ollama

bp = Blueprint('chat', __name__)

@bp.route('/')
def index():
    db = get_db()
    
    print(ollama.get_models())

    return render_template('base.html', title='DeepChat', models=ollama.get_models())