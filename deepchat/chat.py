from collections.abc import Generator
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from deepchat.db import get_db

from . import ollama

bp = Blueprint('chat', __name__)

@bp.route('/')
def index() -> str:
    db = get_db()
    
    print(ollama.get_models())

    return render_template('base.html', title='DeepChat', models=ollama.get_models())

@bp.route('/request', methods=('POST',))
def do_prompt() -> Generator[str, None, None] | str:
    data = request.get_json()
    try:
        model = data['model']
        prompt = data['prompt']
    except KeyError:
        return {"error": "Invalid request"}, 400
    db = get_db()
    response = ollama.generate_response(model, prompt, current_app.app_context())
    return response