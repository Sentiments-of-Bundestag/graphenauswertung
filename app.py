from flask import Flask, jsonify
from flask_cors import CORS
from neo import Database
from flask import request

app = Flask(__name__)
CORS(app)


db = Database("bolt://localhost:7687", "neo4j", "graphenauswertung")
db.seed()

@app.route('/')
def get_persons():
  return jsonify(db.getPersons())

@app.route('/ranked')
def get_persons_ranked():
  return jsonify(db.getPersonsWithRank(request.args.get('filter')))

@app.route('/messages')
def get_messages():
  return jsonify(db.getMessages(request.args.get('filter')))

@app.route('/sentiment')
def get_avg_sentiment():
  return jsonify(db.getAvgSentiment())


app.run(debug=True, host='0.0.0.0')
