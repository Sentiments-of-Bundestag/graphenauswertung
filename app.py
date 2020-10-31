from flask import Flask, jsonify
from flask_cors import CORS
from neo import HelloWorldExample

app = Flask(__name__)
CORS(app)


greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "graphenauswertung")
greeter.seed()

@app.route('/')
def get_persons():
  return jsonify(greeter.getPersons())

@app.route('/sentiment')
def get_messages():
  return jsonify(greeter.getAvgSentiment())


app.run(debug=True, host='0.0.0.0')
