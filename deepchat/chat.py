from collections.abc import Generator
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from uuid import uuid4

from markupsafe import Markup

from .utility import template
from . import ollama
from .db import get_messages, putMessageInDB

bp = Blueprint('chat', __name__)

@bp.route('/')
def index() -> str:
    return redirect(f"/{uuid4()}", code=302)
    return template(current_app.app_context(), 'base.html')

@bp.route('/<string:chat_id>')
def chat(chat_id: str) -> str:
    messages = get_messages(chat_id)

    msgs = Markup("")
    for message, isUser in messages:
        msgs += Markup(f"<div class='{'user-message' if isUser else 'bot-message'}'>")
        msgs += Markup("<p>")
        msgs += message
        msgs += Markup("</p>")
        msgs += Markup("</div>")

    return template(current_app.app_context(), 'base.html', chat_box=msgs, chat_id=chat_id)

@bp.route('/request_v2/<string:chat_id>', methods=('POST',))
def do_prompt(chat_id: str) -> Generator[str, None, None] | str:
    #data = request.get_json()
    #print(f"Got prompt request with data {data}")
    try:
        model = request.form.get('model')
        prompt = request.form.get('user_input')
        history = []#data['history']
    except KeyError:
        return {"error": "Invalid request"}, 400
    db_gen = ""
    response = ollama.generate_response(model, prompt, history, current_app.app_context(), chat_id)
    return Response(response, content_type='text/event-stream')


@bp.route('/request_v1/<string:chat_id>', methods=('POST',))
def do_old_prompt(chat_id: str) -> Generator[str, None, None] | str:
    data = request.get_json()
    print(f"Got prompt request with data {data}")
    try:
        model = data['model']
        prompt = data['prompt']
        history = data['history']
    except KeyError:
        return {"error": "Invalid request"}, 400
    db_gen = ""
    response = ollama.generate_response(model, prompt, history, current_app.app_context(), chat_id)
    return response, {"Content-Type": "text/plain"}