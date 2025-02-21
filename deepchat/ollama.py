import requests
from flask import current_app
import json
from collections.abc import Generator

def build_target(api) -> str:
    with current_app.app_context():
        uri = "http://"
        uri += current_app.config['TARGET_IP']
        uri += ":"
        uri += str(current_app.config['TARGET_PORT'])
        uri += "/"
        uri += api
    return uri

def get_models() -> tuple[str, bool]:
    response = requests.get(build_target("api/tags"), stream=False)
    models = []
    json = response.json()['models']
    for model in json:
        models.append((model['name'], model['name'] == current_app.config['DEFAULT_MODEL']))
    models.sort()
    return models

def prepare_messages(prompt: str, history: list[str, bool]) -> str:
    msgs = []
    for message, isUser in history:
        msgs.append({"content": message, "role": "user" if isUser else "assistant"})
    msgs.append({"content": prompt, "role": "user"})
    return msgs

def generate_response(model, prompt, history, appctx, callback) -> Generator[str, None, None]:
    session = requests.Session()
    data = {"model": model, "messages": prepare_messages(prompt, history)}
    print("Starting generation with data: " + str(data))
    with appctx:
        url = build_target("api/chat")
    with session.post(url, json=data, stream=True) as request:
        for chunk in request.iter_lines():
            data = json.loads(chunk)
            print(data)
            if (data.get('error') != None):
                yield f"Error: {data['error']}"
            elif data['done'] == True:
                callback(data.get('message').get('content'));
                yield f"<<~{data['done_reason']}~>>"
            else:
                callback(data.get('message').get('content')) 
                yield data.get('message').get('content')