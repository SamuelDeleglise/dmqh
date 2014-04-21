import json

from flask import Flask, request
from dmqh import best_move
app = Flask(__name__)


@app.route('/')
def home():
    f = open('static/index.html')
    return f.read()


@app.route('/guess', methods=['POST'])
def guess():
    game_state = json.loads(request.form['game_state'])
    key = best_move(game_state['grid'])
    return key

if __name__ == '__main__':
    app.run(host='0.0.0.0')
