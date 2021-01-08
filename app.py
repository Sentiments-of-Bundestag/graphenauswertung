from flask import Flask, jsonify, request
from flask_cors import CORS

from database.Group5Database import setup_group5_db
from database.Group4Database import setup_group4_db

from dotenv import load_dotenv

load_dotenv(verbose=True)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)

group4_db = setup_group4_db()
group5_db = setup_group5_db()
group5_db.group4_db = group4_db

QUERY_PARAM_FILTER = 'filter'
QUERY_PARAM_SESSION = 'session'


# GROUP 4 endpoints
@app.route('/persons')
def get_persons():
    return jsonify(group4_db.get_persons(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/persons/messages')
def get_messages():
    return jsonify(group4_db.get_messages(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/persons/graph')
def get_persons_graph():
    return jsonify(group4_db.get_graph(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/persons/ranked')
def get_persons_ranked():
    return jsonify(
        group4_db.get_persons_ranked(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/persons/sentiment/key_figures')
def get_key_figures_persons():
    return jsonify(group4_db.get_key_figures(session_id=request.args.get(QUERY_PARAM_SESSION)))


# GROUP 5 endpoints
@app.route('/factions')
def get_factions():
    return jsonify(group5_db.get_factions())


@app.route('/factions/graph')
def get_faction_graph():
    return jsonify(group5_db.get_graph(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/factions/ranked')
def get_factions_ranked():
    return jsonify(
        group5_db.get_factions_ranked(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/factions/sentiment/key_figures')
def get_key_figures_factions():
    return jsonify(group5_db.get_key_figures(session_id=request.args.get(QUERY_PARAM_SESSION)))


# MIXED endpoints
@app.route('/sessions')
def get_sessions():
    return jsonify(group4_db.get_sessions())


@app.route('/sessions/<id>')
def get_session(id):
    return jsonify(group4_db.get_session(id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
