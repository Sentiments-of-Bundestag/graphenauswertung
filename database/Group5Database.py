from neo4j import GraphDatabase
from os import getenv

NODE_FRACTION = 'Faction'


class Group5Database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_fractions(self):
        with self.driver.session() as session:
            fractions = session.run("MATCH (n:{}) RETURN n".format(NODE_FRACTION))
            arr = []
            for fraction in fractions:
                arr.append({
                    'name': fraction.data()['n']['name'],
                    'size': fraction.data()['n']['size']
                })
            return arr

    def get_sentiment(self, f1, f2):
        with self.driver.session() as session:
            query = 'MATCH p=(sender:Faction {{name:"{0}"}})-[r:COMMENTED ]->(receiver:Faction {{name:"{1}"}}) ' \
                    'with sum(r.weight) as weightsum, collect(r.polarity) as sentimentlist, ' \
                    'collect(r.weight) as weightlist unwind weightlist as weights unwind sentimentlist as sentiments ' \
                    'RETURN sum((weights/weightsum)*sentiments) as sentiment'.format(f1, f2)
            sentiment = session.run(query)
            return sentiment.data()[0]['sentiment']

    def get_graph(self):
        with self.driver.session() as session:
            fractions = self.get_fractions()
            messages = []
            for fraction in fractions:
                for other in fractions:
                    fraction_name = fraction['name']
                    other_name = other['name']
                    if fraction_name is not other_name:
                        sentiment = self.get_sentiment(fraction_name, other_name)
                        messages.append({
                            'from': fraction_name,
                            'to': other_name,
                            'sentiment': sentiment
                        })

            return {
                'fractions': fractions,
                'messages': messages
            }



def setup_group5_db():
    database_url = getenv('GROUP5_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP5_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP5_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group5Database(database_url, database_user, database_password)
    return db
