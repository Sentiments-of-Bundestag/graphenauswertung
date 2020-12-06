from time import sleep

from flask import Flask
from flask_cors import CORS
from flask import request
import json

from database.Group5Database import setup_group5_db
from database.MockDatabase import setup_mock_db
from database.Group4Database import setup_group4_db

from dotenv import load_dotenv
load_dotenv(verbose=True)

app = Flask(__name__)
CORS(app)

sleep(10)

mock_db = setup_mock_db()
group4_db = setup_group4_db()
group5_db = setup_group5_db()


# GROUP 4 endpoints
@app.route('/persons')
def get_persons():
    return json.dumps(group4_db.get_persons(), ensure_ascii=False)


# GROUP 5 endpoints
@app.route('/fractions')
def get_fractions():
    return json.dumps(group5_db.get_fractions(), ensure_ascii=False)


@app.route('/fractions/graph')
def get_fraction_graph():
    return json.dumps(group5_db.get_graph(), ensure_ascii=False)


# MOCK ENDPOINTS
@app.route('/mock/persons')
def get_mock_persons():
    return json.dumps(mock_db.get_persons(), ensure_ascii=False)


@app.route('/mock/ranked')
def get_mock_persons_ranked():
    return json.dumps(mock_db.get_persons_with_rank(request.args.get('filter')), ensure_ascii=False)


@app.route('/mock/messages')
def get_mock_messages():
    return json.dumps(mock_db.get_messages(request.args.get('filter')), ensure_ascii=False)


@app.route('/mock/sentiment')
def get_mock_avg_sentiment():
    return json.dumps(mock_db.get_avg_sentiment(), ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
