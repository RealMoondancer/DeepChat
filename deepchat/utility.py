from flask import render_template, current_app
from flask.ctx import AppContext
from . import ollama

def template(ctx: AppContext, template: str, **kwargs) -> str:
    with ctx:
        models = ollama.get_models()
        title = current_app.config['TITLE']
    return render_template(template, title=title, models=models, **kwargs)