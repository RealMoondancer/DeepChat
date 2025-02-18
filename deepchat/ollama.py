import requests
from flask import current_app
import json

def build_target(api):
    with current_app.app_context():
        uri = "http://"
        uri += current_app.config['TARGET_IP']
        uri += ":"
        uri += str(current_app.config['TARGET_PORT'])
        uri += "/"
        uri += api
    return uri

def get_models():
    response = requests.get(build_target("api/tags"), stream=False)
    models = []
    json = response.json()['models']
    for model in json:
        models.append((model['name'], model['name'] == current_app.config['DEFAULT_MODEL']))
    models.sort()
    return models

def generate_response(model, prompt, appctx, stream=True):
    session = requests.Session()
    data = {"model": model, "prompt": prompt, "stream": stream}
    print("Starting generation with data: " + str(data))
    with appctx:
        url = build_target("api/generate")
    with session.post(url, stream=stream, json=data) as request:
        if stream:
            for chunk in request.iter_lines():
                data = json.loads(chunk)
                if data['done'] == True:
                    yield f"<<~{data['done_reason']}~>>"
                yield data['response']
        else:
            yield request.json()['response']