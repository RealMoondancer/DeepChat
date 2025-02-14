import os

import requests
from flask import Flask, Response, request, g
import sqlite3
import json
from uuid import uuid4


DATABASE = 'db.sqlite3'

TARGET = {
    "ip": "10.56.60.171",
    #"ip": "localhost",
    "port": 11434,
    "api": "/api/generate"
}

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'asdf123'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        

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
    mimetype = mimetypes.get(ext, None)
    if mimetype is not None:
        # Serve css html and js files
        content = get_file(complete_path)
        return Response(content, mimetype=mimetype)
    # Requests for chat ids
    cur = get_db().cursor()
    # TODO escape stuff
    cur.execute("SELECT * FROM chats WHERE id=?", (path,))
    row = cur.fetchone()
    if row is None:
        return Response("Chat not found", status=404)
    
    cur.execute("SELECT * FROM messages WHERE chatId=?", (path,))
    msgs = cur.fetchall()
    
    
    # PAIN
    # Replace <!--<<~>>--> with script tag to insert messages
    content = get_file('index.html')
    msgs_str = """<script>
    var messages = {"""
    for msg in msgs:
        msgs_str += f'"{msg[1].replace("\r\n", "\\r\\n")}": "{msg[3]}",' # 1: content 3: isUser?
    
    msgs_str = msgs_str[:-1] # Remove last comma
    msgs_str += """};
    for (const [key, value] of Object.entries(messages)) {
        (addMessage("", value === '1')).querySelector("#messageText").textContent = key;
    }
    </script>"""
    content = content.replace("<!--<<~>>-->", msgs_str)
    return Response(content, mimetype="text/html")
    

@app.route('/request', methods=['POST'])
def handle_request():
    prompt = request.get_json()
    print(f"Got request with data: {prompt}")

    data = {"model": "deepseek-r1:1.5b", "prompt": prompt['prompt'], "options": {"num_ctx": 1024}}
    url = 'http://' + TARGET["ip"] + ':' + str(TARGET["port"]) + TARGET["api"]
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


app.run(host='0.0.0.0', port=8443)