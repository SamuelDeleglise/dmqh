from flask import Flask
app = Flask(__name__)


@app.route('/')
def home():
    f = open('static/index.html')
    return f.read()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
