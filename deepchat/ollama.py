import requests
from flask import current_app

def build_target(api):
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