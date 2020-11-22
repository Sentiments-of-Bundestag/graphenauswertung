from neo import Database
from time import sleep
from os import environ


def setup_db():
    database_url = environ['DATABASE_URL']
    if database_url is None:
        database_url = 'bolt://localhost:7687'

    database_user = environ['DATABASE_USER']
    if database_user is None:
        database_user = 'neo4j'

    database_password = environ['DATABASE_PASSWORD']
    if database_password is None:
        database_password = 'graphenauswertung'

    print(database_url)
    print(database_user)
    print(database_password)

    sleep(20)

    db = Database(database_url, database_user, database_password)
    db.seed()
    return db
