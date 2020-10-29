from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
  return 'Hello, World!'


app.run(debug=True, host='0.0.0.0')
