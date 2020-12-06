from neo4j import GraphDatabase
from os import getenv

NODE_PERSON = 'Person'


class Group4Database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_persons(self):
        with self.driver.session() as session:
            persons = session.run("MATCH (n:{}) RETURN n".format(NODE_PERSON))
            arr = []
            for person in persons:
                arr.append({
                    'name': person.data()['n']['name'],
                    'speakerId': person.data()['n']['speakerId'],
                    'role': person.data()['n']['role'],
                })
            return arr


def setup_group4_db():
    database_url = getenv('GROUP4_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP4_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP4_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group4Database(database_url, database_user, database_password)
    return db
