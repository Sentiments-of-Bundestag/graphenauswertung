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

### `/sessions`

returns all available parliament sessions.
The `sessionId` can be used to filter other endpoints (see below).

#### Sample Data

```json
[
  {
    "sessionId": 138, 
    "legislativePeriod": 19, 
    "endDateTime": "2019-12-20T15:39:00+00:00", 
    "startDateTime": "2019-12-20T09:00:00+00:00"
  }
]
```

### `/factions`

returns all factions from group5 database

#### Sample Data
```json
[
  {
    "name": "CDU/CSU", 
    "size": 246,
    "factionId": "F000"
  }, 
  {
    "name": "SPD", 
    "size": 152,
    "factionId": "F001"
  }
]
```

### `/factions/graph`

returns the faction graph based on the group5 database

#### Query Parameters

| Name    | Description                                                        | Allowed Values               |
|---------|--------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages to only those from the given session           | any sessionId from `/sessions` |

#### Sample Data
```json
{
  "factions": [
    {
      "name": "CDU/CSU",
      "size": 246,
      "factionId": "F000"
    },
    {
      "name": "SPD",
      "size": 152,
      "factionId": "F001"
    }
  ],
  "messages": [
    {
      "recipient": "F001",
      "sender": "F000",
      "sentiment": -1.399999976158142,
      "count": 10
    },
    {
      "recipient": "F000",
      "sender": "F001",
      "sentiment": 0.1,
      "count": 2 
    }
  ]
}

```

### `/factions/ranked`

returns the page-ranked factions from group5 database

#### Query Parameters

| Name    | Description                                                                                       | Allowed Values               |
|---------|---------------------------------------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages used for page rank calculation to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages used for page rank calculation to only those from the given session           | any sessionId from `/sessions` |


#### Sample Data
```json
[
  {
    "name": "CDU/CSU", 
    "size": 246,
    "factionId": "F000",
    "rank": "0.7"
  }, 
  {
    "name": "SPD", 
    "size": 152,
    "factionId": "F001",
    "rank": "0.3"
  }
]
```

### `/persons`

returns all persons from group4 database

#### Query Parameters

| Name    | Description                                                                             | Allowed Values               |
|---------|-----------------------------------------------------------------------------------------|------------------------------|
| filter  | Limits the persons to only those connected to messages with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the persons to only those connected to messages in the given session             | any sessionId from `/sessions` |

#### Sample Data
```json
[
    {
      "faction": "CDU/CSU", 
      "name": "Frank Heinrich", 
      "role": "Platzhalter", 
      "speakerId": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7"
    }, 
    {
      "faction": "SPD", 
      "name": "Frank Schwabe", 
      "role": "Platzhalter", 
      "speakerId": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112"
    }
]
```


### `persons/messages`

returns all messages from group4 database

#### Query Parameters

| Name    | Description                                                        | Allowed Values               |
|---------|--------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages to only those from the given session           | any sessionId from `/sessions` |

#### Sample Data
```json
[
    {
      "count": 2, 
      "recipient": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sender": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sentiment": -0.2
    },
    {
      "count": 4, 
      "recipient": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sender": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sentiment": 0.1
    }
  ]
```

### `persons/graph`

returns the person graph based on the group4 database

#### Query Parameters

| Name    | Description                                                                                                                                             | Allowed Values               |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment and the persons to only those connected to messages with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages to only those from the given session the persons to only those connected to messages in the given session                           | any sessionId from `/sessions` |

#### Sample Data
```json
{
  "persons": [
    {
      "faction": "CDU/CSU", 
      "factionId": "F000",
      "name": "Frank Heinrich", 
      "role": "Platzhalter", 
      "speakerId": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7"
    }, 
    {
      "faction": "SPD",  
      "factionId": "F001",
      "name": "Frank Schwabe", 
      "role": "Platzhalter", 
      "speakerId": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112"
    }
  ],
  "messages": [
    {
      "count": 2, 
      "recipient": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sender": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sentiment": -0.2
    },
    {
      "count": 4, 
      "recipient": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sender": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sentiment": 0.1
    }
  ]
}
```

### `persons/ranked`

returns the page-ranked persons from group4 database

#### Query Parameters

| Name    | Description                                                                                       | Allowed Values               |
|---------|---------------------------------------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages used for page rank calculation to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages used for page rank calculation to only those from the given session           | any sessionId from `/sessions` |

#### Sample Data
```json
[
  {
    "faction": "DIE LINKE",
    "factionId": "F003", 
    "name": "Caren Lay", 
    "rank": 0.029715244473085708, 
    "role": "Platzhalter", 
    "speakerId": "MDB-c3f825cc-9b63-4241-85f9-df425f0c6486"
  }, 
  {
    "faction": "CDU/CSU",    
    "factionId": "F000",
    "name": "Wolfgang Schäuble", 
    "rank": 0.029176551464191278, 
    "role": "Platzhalter", 
    "speakerId": "MDB-fd366231-9c25-416b-8604-e934d956e177"
  }
]
```