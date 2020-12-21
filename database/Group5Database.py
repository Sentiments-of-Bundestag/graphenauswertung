from os import getenv

from database.Database import Database
from pagerank import calculate_pagerank_eigenvector

NODE_FACTION = 'Faction'
REL_COMMENTED = 'COMMENTED'


class Group5Database(Database):
    group4_db = None

    def get_factions(self):
        with self.driver.session() as session:
            factions = session.run("MATCH (n:{}) RETURN n.name as name, n.size as size".format(NODE_FACTION))
            group4_factions = self.group4_db.get_factions()
            arr = []
            for faction in factions:
                group4_faction = next(
                    (f for f in group4_factions if
                     f['name'].replace(" ", "") == faction.data()['name'].replace(" ", "")), None)
                fac = {
                    'name': faction.data()['name'],
                    'size': faction.data()['size']
                }
                if group4_faction is not None:
                    fac['factionId'] = group4_faction['factionId']
                arr.append(fac)
            return arr

    def get_message(self, f1, f2, sentiment_type="NEUTRAL", session_id=None):
        s = None
        where = ""

        if session_id is not None:
            s = self.group4_db.get_session(session_id)

        if s is not None:
            session_date = s['startDateTime'].split('T')[0]
            where = "WHERE split(r.date, 'T')[0] = '{0}'".format(session_date)

        if sentiment_type == 'POSITIVE':
            if len(where) == 0:
                where = "WHERE "
            else:
                where = where + " AND "
            where = where + "r.polarity > 0 "

        if sentiment_type == 'NEGATIVE':
            if len(where) == 0:
                where = "WHERE "
            else:
                where = where + " AND "
            where = where + "r.polarity < 0 "

        with self.driver.session() as session:
            query = 'MATCH p=(sender:{0} {{name:"{2}"}})-[r:{1} ]->(receiver:{0} {{name:"{3}"}}) ' \
                    '{4}' \
                    'with r as r, sum(r.weight) as weightsum, collect(r.polarity) as sentimentlist, ' \
                    'collect(r.weight) as weightlist unwind weightlist as weights unwind sentimentlist as sentiments ' \
                    'RETURN sum((weights/weightsum)*sentiments) as sentiment, count(r) as count' \
                .format(NODE_FACTION, REL_COMMENTED, f1, f2, where)

            sentiment = session.run(query)
            return sentiment.data()[0]

    def get_graph(self, sentiment_type="NEUTRAL", session_id=None):
        factions = self.get_factions()
        messages = []
        for faction in factions:
            for other in factions:
                faction_name = faction['name']
                other_name = other['name']
                if faction_name is not other_name:
                    message = self.get_message(faction_name, other_name, sentiment_type, session_id)
                    if message['count'] > 0:
                        messages.append({
                            'sender': faction['factionId'],
                            'recipient': other['factionId'],
                            'sentiment': message['sentiment'],
                            'count': message['count']
                        })

        return {
            'factions': factions,
            'messages': messages
        }

    def get_messages(self, sentiment_type="NEUTRAL", session_id=None):
        result = self.get_graph(sentiment_type, session_id)
        return result['messages']

    def get_factions_ranked(self, sentiment_type, session_id=None):
        factions = self.get_factions()
        messages = self.get_messages(sentiment_type, session_id)
        ranked = calculate_pagerank_eigenvector(factions, messages, field_name='factionId')
        return sorted(ranked, key=lambda x: x['rank'], reverse=True)


def setup_group5_db():
    database_url = getenv('GROUP5_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP5_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP5_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group5Database(database_url, database_user, database_password)
    return db
