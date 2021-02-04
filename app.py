from flask import Flask, jsonify, request
from flask_cors import CORS
from cache import Cache

from database.Group5Database import setup_group5_db
from database.Group4Database import setup_group4_db

from dotenv import load_dotenv

load_dotenv(verbose=True)

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app_cache = Cache(app, 'simple' if __name__ == '__main__' else 'redis')
cache = app_cache.cache

CORS(app)

group4_db = setup_group4_db()
group5_db = setup_group5_db()
group5_db.group4_db = group4_db

QUERY_PARAM_FILTER = 'filter'
QUERY_PARAM_SESSION = 'session'
QUERY_PARAM_PERSON = 'person'
QUERY_PARAM_REVERSE = 'reverse'
QUERY_PARAM_EXCLUDE_APPLAUSE = 'excludeApplause'


def generate_cache_key():
    return app_cache.generate_cache_key(request)


# GROUP 4 endpoints
@app.route('/persons')
@cache.cached(make_cache_key=generate_cache_key)
def get_persons():
    return jsonify(group4_db.get_persons(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                         request.args.get(QUERY_PARAM_PERSON)))


@app.route('/persons/messages')
@cache.cached(make_cache_key=generate_cache_key)
def get_messages():
    return jsonify(group4_db.get_messages(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                          request.args.get(QUERY_PARAM_PERSON),
                                          request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/persons/graph')
@cache.cached(make_cache_key=generate_cache_key)
def get_persons_graph():
    return jsonify(group4_db.get_graph(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                       request.args.get(QUERY_PARAM_PERSON),
                                       request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/persons/ranked')
@cache.cached(make_cache_key=generate_cache_key)
def get_persons_ranked():
    return jsonify(
        group4_db.get_persons_ranked(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                     request.args.get(QUERY_PARAM_REVERSE) == 'true',
                                     request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/persons/sentiment/key_figures')
@cache.cached(make_cache_key=generate_cache_key)
def get_key_figures_persons():
    return jsonify(group4_db.get_key_figures(session_id=request.args.get(QUERY_PARAM_SESSION),
                                             exclude_applause=request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


# GROUP 5 endpoints
@app.route('/factions')
@cache.cached(make_cache_key=generate_cache_key)
def get_factions():
    return jsonify(group5_db.get_factions(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION)))


@app.route('/factions/graph')
@cache.cached(make_cache_key=generate_cache_key)
def get_faction_graph():
    return jsonify(group5_db.get_graph(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                       request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/factions/ranked')
@cache.cached(make_cache_key=generate_cache_key)
def get_factions_ranked():
    return jsonify(
        group5_db.get_factions_ranked(request.args.get(QUERY_PARAM_FILTER), request.args.get(QUERY_PARAM_SESSION),
                                      request.args.get(QUERY_PARAM_REVERSE) == 'true',
                                      request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/factions/sentiment/key_figures')
@cache.cached(make_cache_key=generate_cache_key)
def get_key_figures_factions():
    return jsonify(group5_db.get_key_figures(session_id=request.args.get(QUERY_PARAM_SESSION),
                                             exclude_applause=request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


@app.route('/factions/proportions')
@cache.cached(make_cache_key=generate_cache_key)
def get_faction_proportions():
    return jsonify(group5_db.get_faction_proportions(request.args.get(QUERY_PARAM_SESSION),
                                                     request.args.get(QUERY_PARAM_EXCLUDE_APPLAUSE) == 'true'))


# MIXED endpoints
@app.route('/sessions')
@cache.cached()
def get_sessions():
    return jsonify(group4_db.get_sessions())


@app.route('/sessions/<id>')
@cache.memoize()
def get_session(id):
    return jsonify(group4_db.get_session(id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
