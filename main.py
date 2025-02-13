import os

import requests
from flask import Flask, Response, request
from flask_socketio import SocketIO
import json

target = {
    #"ip": "10.56.60.171",
    "ip": "localhost",
    "port": 11434,
    "api": "/api/generate"
}

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'asdf123'

socketio = SocketIO(app)


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)


@app.route('/', methods=['GET'])
def metrics():  # pragma: no cover
    content = get_file('index.html')
    return Response(content, mimetype="text/html")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join(root_dir(), path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)

@app.route('/request', methods=['POST'])
def handle_request():
    prompt = request.get_json()
    print(f"Got request with data: {prompt}")

    data = {"model": "deepseek-r1:1.5b", "prompt": prompt['prompt'], "options": {"num_ctx": 1024}}
    url = 'http://' + target["ip"] + ':' + str(target["port"]) + target["api"]
    # Request to target
    print("Requesting to " + url)
    resp = stream_req(url, data)
    
    return resp, {"Content-Type": "text/plain"}

def stream_req(url, data):
    sess = requests.Session()
    with sess.post(url, stream=True, headers=None, json=data) as req:
        for chunk in req.iter_lines():
            # Parse json
            try:
                data = json.loads(chunk)
                print(data)
                if data['done'] == True:
                    return f"<<~{data['done_reason']}~>>"
                yield data['response']
            except Exception as e:
                print(f"Failed to parse {chunk}")
                print(e)

@socketio.on('connect')
def connect():
    print("Client connected")
    socketio.emit('hello', {'data': 'Hello'})

socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=8443)