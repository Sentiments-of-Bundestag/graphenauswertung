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
    "factionId": "F000",
    "sessionIds": [ 46, 100]
  }, 
  {
    "name": "SPD", 
    "size": 152,
    "factionId": "F001",
    "sessionIds": [ 46 ]
  }
]
```

### `/factions/graph`

returns the faction graph based on the group5 database. 
Messages are aggregated so that there is only one entry for a unique (directed) relationship between sender and recipient.
The `count` is the total number of messages that were aggregated to the entry. 
The `sentiment` is the sum of the sentiments of all messages that were aggregated to the entry. 

#### Query Parameters

| Name    | Description                                                        | Allowed Values               |
|---------|--------------------------------------------------------------------|------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`       |
| session | Limits the messages to only those from the given session           | any sessionId from `/sessions` |
| exclude_applause | Filters out all messages which are flagged as applause    | `true`                       |

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
      "count": 10,
      "sessionIds": [46, 100]
    },
    {
      "recipient": "F000",
      "sender": "F001",
      "sentiment": 0.1,
      "count": 2,
      "sessionIds": [46, 100]
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
| reverse | Uses the ''Reverse PageRank'' for page rank calculation                                           | `true`                       |
| exclude_applause | Filters out all messages which are flagged as applause                                   | `true`                       |


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

### `/factions/proportions`

returns speech proportions of each faction in percentage, regarding all sessions.

| Name    | Description                                                                                       | Allowed Values                 |
|---------|---------------------------------------------------------------------------------------------------|--------------------------------|
| session | Limits the messages used for proportion calculation to only those from the given session          | any sessionId from `/sessions` |
| exclude_applause | Filters out all messages which are flagged as applause                                   | `true`                       |

#### Sample Data
```json
[
  {
    "factionId": "F000",
    "name": "CDU/CSU",
    "proportion": 24.664010828634297,
    "size": 246
  },
  {
    "factionId": "F001",
    "name": "SPD",
    "proportion": 20.437122713830245,
    "size": 152
  }
]
```

### `factions/sentiment/key_figures`

returns the calculated key figures of sentiments between all factions

| Name    | Description                                                                                       | Allowed Values                 |
|---------|---------------------------------------------------------------------------------------------------|--------------------------------|
| session | Limits the messages used for key figures calculation to only those from the given session         | any sessionId from `/sessions` |
| exclude_applause | Filters out all messages which are flagged as applause                                   | `true`                       |

#### Sample Data
```json
{
  "highest_sentiment": 16.04166666790843, 
  "lowest_sentiment": 0.5, 
  "sentiment_lower_quartile": 1.0, 
  "sentiment_median": 2.5903602056205273, 
  "sentiment_upper_quartile": 5.3949188850820065
}
```

### `/persons`

returns all persons from group4 database

#### Query Parameters

| Name    | Description                                                                             | Allowed Values                 |
|---------|-----------------------------------------------------------------------------------------|--------------------------------|
| filter  | Limits the persons to only those connected to messages with the given type of sentiment | `POSITIVE`, `NEGATIVE`         |
| session | Limits the persons to only those connected to messages in the given session             | any sessionId from `/sessions` |
| person  | Limits the persons to only the given person                                             | any speakerId from `/persons`  |

#### Sample Data
```json
[
    {
      "faction": "CDU/CSU",
      "factionId": "F000", 
      "name": "Frank Heinrich", 
      "role": "Platzhalter", 
      "speakerId": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7",
      "sessionIds": [ 46, 100 ]
    }, 
    {
      "faction": "SPD", 
      "factionId": "F001",
      "name": "Frank Schwabe", 
      "role": "Platzhalter", 
      "speakerId": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112",
      "sessionIds": [ 46 ]
    }
]
```


### `persons/messages`

returns all messages from group4 database. The messages are not aggregated in any way.

#### Query Parameters

| Name    | Description                                                        | Allowed Values                 |
|---------|--------------------------------------------------------------------|--------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment | `POSITIVE`, `NEGATIVE`         |
| session | Limits the messages to only those from the given session           | any sessionId from `/sessions` |
| person  | Limits the messages to only those from the given person            | any speakerId from `/persons`  |
| exclude_applause | Filters out all messages which are flagged as applause    | `true`                       |

#### Sample Data
```json
[
    {     
      "recipient": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sender": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sentiment": 0.2,
      "sessionId": 46
    },
    {
      "recipient": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sender": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112",
      "sentiment": 0.7, 
      "sessionId": 46
    }
  ]
```

### `persons/graph`

returns the person graph based on the group4 database. 
Messages are aggregated so that there is only one entry for a unique (directed) relationship between sender and recipient.
The `count` is the total number of messages that were aggregated to the entry. 
The `sentiment` is the sum of the sentiments of all messages that were aggregated to the entry. 

#### Query Parameters

| Name    | Description                                                                                                                                             | Allowed Values                 |
|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| filter  | Limits the messages to only those with the given type of sentiment and the persons to only those connected to messages with the given type of sentiment | `POSITIVE`, `NEGATIVE`         |
| session | Limits the messages to only those from the given session the persons to only those connected to messages in the given session                           | any sessionId from `/sessions` |
| person  | Limits the messages to only those from the given person and the persons information to only those connected to the given person                         | any speakerId from `/persons`  |
| exclude_applause | Filters out all messages which are flagged as applause                                                                                         | `true`                       |

#### Sample Data
```json
{
  "persons": [
    {
      "faction": "CDU/CSU", 
      "factionId": "F000",
      "name": "Frank Heinrich", 
      "role": "Platzhalter", 
      "speakerId": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7",
      "sessionIds": [ 46, 100 ]
    }, 
    {
      "faction": "SPD",  
      "factionId": "F001",
      "name": "Frank Schwabe", 
      "role": "Platzhalter", 
      "speakerId": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112",
      "sessionIds": [ 46 ]
    }
  ],
  "messages": [
    {
      "count": 2, 
      "recipient": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sender": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sentiment": -0.2,
      "sessionIds": [ 46, 100 ]
    },
    {
      "count": 4, 
      "recipient": "MDB-24aa7763-e95d-4d1d-834c-de3cae2406d7", 
      "sender": "MDB-c0f339ee-9db1-411d-ad2f-0357e98bf112", 
      "sentiment": 0.1,
      "sessionIds": [ 46 ]
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
| reverse | Uses the ''Reverse PageRank'' for page rank calculation                                           | `true`                       |
| exclude_applause | Filters out all messages which are flagged as applause                                   | `true`                       |

#### Sample Data
```json
[
  {
    "faction": "DIE LINKE",
    "factionId": "F003", 
    "name": "Caren Lay", 
    "rank": 0.029715244473085708, 
    "role": "Platzhalter",
    "sessionIds": [ 46, 100 ],
    "speakerId": "MDB-c3f825cc-9b63-4241-85f9-df425f0c6486"
  }, 
  {
    "faction": "CDU/CSU",    
    "factionId": "F000",
    "name": "Wolfgang Schäuble", 
    "rank": 0.029176551464191278, 
    "role": "Platzhalter",   
    "sessionIds": [ 46   ], 
    "speakerId": "MDB-fd366231-9c25-416b-8604-e934d956e177"
  }
]
```

### `persons/sentiment/key_figures`

returns the calculated key figures of sentiments between all persons

#### Query Parameters

| Name      | Description                                                                                    | Allowed Values                 |
|-----------|------------------------------------------------------------------------------------------------|--------------------------------|
| session   | Limits the messages used for key figures calculation to only those from the given session      | any sessionId from `/sessions` |
| exclude_applause | Filters out all messages which are flagged as applause                                  | `true`                       |


#### Sample Data
```json
{
  "highest_sentiment": 0.6166666666666667,
  "lowest_sentiment": -1,
  "sentiment_lower_quartile": 0.07142857142857142,
  "sentiment_median": 0.5,
  "sentiment_upper_quartile": 0.5
}
```