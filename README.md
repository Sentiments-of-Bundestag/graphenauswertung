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

### `/fractions`

returns all fractions from group5 database

### `/fractions/graph`

returns the fraction graph based on the group5 database

### `/persons`

returns all persons from group4 database

### `/mock/persons`

returns the mock persons from the internal mock database 

### `/mock/ranked`

returns the ranked persons from the internal mock database

### `/mock/messages`

returns the messages from the internal mock database

### `/mock/sentiment`

return the average sentiment over the messages from the internal mock database

