from neo4j import GraphDatabase
from os import getenv

from pagerank import aggregate_messages, pagerank

NODE_PERSON = 'Person'
NODE_FACTION = 'Faction'
NODE_COMMENTARY = 'Commentary'
NODE_SESSION = 'ParliamentSession'
REL_MEMBER = 'MEMBER'
REL_SESSION = 'SESSION'
REL_RECEIVER = 'RECEIVER'
REL_SENDER = 'SENDER'


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

    def get_messages(self):
        with self.driver.session() as session:
            where = ""
            if type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            query = "MATCH (a)-[s:{0}]->(m:{1})-[r:{2}]->(b) {3}" \
                    "RETURN m.sentiment AS sentiment, a.speakerId AS sender, b.speakerId AS recipient".format(
                REL_SENDER, NODE_COMMENTARY, REL_RECEIVER, where)

            messages = session.run(query)
            return messages.data()

    def get_graph(self):
        return {
            'persons': self.get_persons(),
            'messages': aggregate_messages(self.get_messages())
        }

    def get_persons_ranked(self):
        persons = self.get_persons()
        messages = self.get_messages()
        ranked = pagerank(persons, aggregate_messages(messages))
        return sorted(ranked.tolist(), key=lambda x: x['rank'], reverse=True)


def setup_group4_db():
    database_url = getenv('GROUP4_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP4_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP4_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group4Database(database_url, database_user, database_password)
    return db
