import json
import sqlite3
import time
from flask import Flask, render_template, url_for, jsonify, request, g

#import multiprocessing
from multiprocessing import Process, Pipe
from pinterpreter import run
import time

# %%%%%%%%%%%%%%%%%%%%
#       Globals
# %%%%%%%%%%%%%%%%%%%%
app = Flask(__name__)
app.config.from_pyfile('config.py')
STATE = {}
SERVER_PIPE = None
SQL_SCHEMA_PATH = 'schema.sql'
DB_PATH = 'iot.db'

# %%%%%%%%%%%%%%%%%%%%
#       Routes
# %%%%%%%%%%%%%%%%%%%%

# ===== Pages =====
@app.route('/')
def home():
    return render_template("logs.html")

@app.route('/manual')
def logs():
    return render_template("manual.html")

# ===== REST =====
@app.route('/get')
def get():
    key = request.args.get('key', None, type=str)
    try:
        return json.dumps({key: STATE[key]})
    except KeyError:
        return json.dumps({key: None})

@app.route('/put', methods=['POST'])
def put():
    # send a key-value pair to the server
    key = request.form['key']
    value = request.form['value'].strip()
    STATE[key] = value

    if key == 'rfid':
        add_log(value)
        auth(value)
        return json.dumps({key: STATE[key]})

    if key == 'lcd':
        add_message(value)

    cmd = "put "+key+" "+value
    print(cmd)

    SERVER_PIPE.send(cmd)

    return json.dumps({key: STATE[key]})

@app.route('/putbadge', methods=['POST'])
def aj_auth():
    key = request.form['key']
    badge = request.form['value']
    add_auth(badge)
    return json.dumps({key: badge})

@app.route('/rmbadge', methods=['POST'])
def rm_auth():
    key = request.form['key']
    badge = request.form['value']
    print(key, badge)
    rem_auth(badge)
    return json.dumps({key: badge})

@app.route('/getmsg')
def get_msg():
    return json.dumps({'messages': get_messages()})

@app.route('/getlog')
def get_log():
    return json.dumps({'logs': get_logs()})

@app.route('/getauth')
def get_auth():
    return json.dumps({'auths': get_auths()})

@app.route('/getstate')
def get_state():
    return json.dumps(STATE)

# %%%%%%%%%%%%%%%%%%%%
#       Functions
# %%%%%%%%%%%%%%%%%%%%

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def add_log(id_badge):
    # add an entry to the db for loggin badging
    with app.app_context():
        c = get_db().cursor()
        c.execute("INSERT INTO log(date, id_badge) VALUES(?, ?);", (time.strftime("%Y/%m/%d %H:%M:%S"), id_badge))
        c.close()
        get_db().commit()

def get_logs():
    with app.app_context():
        c = get_db().cursor()
        c.execute("SELECT date, id_badge FROM log;")
        res = c.fetchall()
        c.close()
        return res
    
def add_message(message):
    # add an entry to the db for logging messages
    with app.app_context():
        c = get_db().cursor()
        c.execute("INSERT INTO messages(date, message) VALUES(?, ?);", (time.strftime("%Y/%m/%d %H:%M:%S"), message))
        c.close()
        get_db().commit()

def get_messages():
    with app.app_context():
        c = get_db().cursor()
        c.execute("SELECT date, message FROM messages;")
        res = c.fetchall()
        c.close()
        return res

def add_auth(id_badge):
    # add an entry to the db for logging messages
    with app.app_context():
        c = get_db().cursor()
        c.execute("INSERT INTO autorise(id_badge) VALUES(?);", (id_badge, ))
        c.close()
        get_db().commit()

def rem_auth(id_badge):
    with app.app_context():
        c = get_db().cursor()
        c.execute("DELETE FROM autorise WHERE id_badge IS ?;", (id_badge, ))
        c.close()
        get_db().commit()


def get_auths():
    # returns the list of authorized rfid badges
    with app.app_context():
        c = get_db().cursor()
        c.execute("SELECT id_badge FROM autorise;")
        res = list([x[0] for x in c.fetchall()])
        c.close()
        return res

def auth(id_badge):
    # return true if id_badge is in the DB
    if id_badge in get_auths():
        SERVER_PIPE.send("ident_ok")
    else:
        SERVER_PIPE.send("ident_er")


# %%%%%%%%%%%%%%%%%%%%
#       Main
# %%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
    # db creation
    init_db()

    interpreter_pipe, SERVER_PIPE = Pipe(False)
    p = Process(target=run, args=(interpreter_pipe,))
    p.start()

    app.run(host='0.0.0.0', port=5000)
