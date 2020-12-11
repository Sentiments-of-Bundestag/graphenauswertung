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

### Start the Mock DB

docker-compose up

### Visit the browser

http://localhost:7474/browser

username: neo4j
password: graphenauswertung

### Empty the database

```MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r```

## Endpoints

Method: `GET` for all

### `/factions`

returns all factions from group5 database

### `/factions/graph`

returns the faction graph based on the group5 database

### `/persons`

returns all persons from group4 database

### `persons/messages`

returns all messages from group4 database

### `persons/graph`

returns the person graph based on the group4 database

### `persons/ranked`

returns the page-ranked persons from group4 database