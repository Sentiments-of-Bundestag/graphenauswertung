# graphenauswertung

## Prerequisites

* Python3
* venv

## Install the requirements
```pip install -r requirements.txt```

## Running the App
```python app.py```

App runs on http://localhost:5000.

## Run a local Neo4j database

### Prerequisites

Docker

### Start the DB

docker-compose up

### Visit the browser

http://localhost:7474/browser

username: neo4j
password: graphenauswertung

### Empty the database

```MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r```
