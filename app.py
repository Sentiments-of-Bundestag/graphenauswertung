from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from time import sleep
from setup_db import setup_db

app = Flask(__name__)
CORS(app)

sleep(10)

db = setup_db()


@app.route('/')
def get_persons():
    return jsonify(db.get_persons())


@app.route('/ranked')
def get_persons_ranked():
    return jsonify(db.get_persons_with_rank(request.args.get('filter')))


@app.route('/messages')
def get_messages():
    return jsonify(db.get_messages(request.args.get('filter')))


@app.route('/sentiment')
def get_avg_sentiment():
    return jsonify(db.get_avg_sentiment())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
