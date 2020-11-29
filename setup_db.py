from neo import Database
from time import sleep
from os import getenv


def setup_db():
    database_url = getenv('DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('DATABASE_USER', 'neo4j')
    database_password = getenv('DATABASE_PASSWORD', 'graphenauswertung')

    print(database_url)
    print(database_user)
    print(database_password)

    sleep(20)

    db = Database(database_url, database_user, database_password)
    db.seed()
    return db
