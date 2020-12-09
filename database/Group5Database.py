from os import getenv

from database.Database import Database

NODE_FACTION = 'Faction'
REL_COMMENTED = 'COMMENTED'


class Group5Database(Database):

    def get_factions(self):
        with self.driver.session() as session:
            factions = session.run("MATCH (n:{}) RETURN n".format(NODE_FACTION))
            arr = []
            for faction in factions:
                arr.append({
                    'name': faction.data()['n']['name'],
                    'size': faction.data()['n']['size']
                })
            return arr

    def get_sentiment(self, f1, f2):
        with self.driver.session() as session:
            query = 'MATCH p=(sender:{0} {{name:"{2}"}})-[r:{1} ]->(receiver:{0} {{name:"{3}"}}) ' \
                    'with sum(r.weight) as weightsum, collect(r.polarity) as sentimentlist, ' \
                    'collect(r.weight) as weightlist unwind weightlist as weights unwind sentimentlist as sentiments ' \
                    'RETURN sum((weights/weightsum)*sentiments) as sentiment'.format(NODE_FACTION, REL_COMMENTED, f1, f2)
            sentiment = session.run(query)
            return sentiment.data()[0]['sentiment']

    def get_graph(self):
        factions = self.get_factions()
        messages = []
        for faction in factions:
            for other in factions:
                faction_name = faction['name']
                other_name = other['name']
                if faction_name is not other_name:
                    sentiment = self.get_sentiment(faction_name, other_name)
                    messages.append({
                        'from': faction_name,
                        'to': other_name,
                        'sentiment': sentiment
                    })

        return {
            'factions': factions,
            'messages': messages
        }


def setup_group5_db():
    database_url = getenv('GROUP5_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP5_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP5_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group5Database(database_url, database_user, database_password)
    return db
