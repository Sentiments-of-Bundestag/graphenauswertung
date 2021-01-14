from os import getenv
import numpy as np

from database.Database import Database
from pagerank import calculate_pagerank_eigenvector

NODE_FACTION = 'Faction'
REL_COMMENTED = 'COMMENTED'


class Group5Database(Database):
    group4_db = None

    def get_factions(self, sentiment_type="NEUTRAL", session_id=None):
        where = self.get_where_clause(sentiment_type, session_id)
        with self.driver.session() as session:
            query = "MATCH (sender:{0})-[r:{1}]-(recipient:{0}) " \
                    "{2} " \
                    "with sender, collect(distinct r.sessionId) as sessionList, " \
                    "collect(r) as rlist unwind rlist as r " \
                    "RETURN DISTINCT sender.name as name, sender.size as size, sender.factionId as factionId, " \
                    "sessionList as sessionIds" \
                .format(NODE_FACTION, REL_COMMENTED, where)
            print(query)
            factions = session.run(query)
            return factions.data()

    def get_graph(self, sentiment_type="NEUTRAL", session_id=None):
        factions = self.get_factions(sentiment_type, session_id)
        messages = self.get_messages(sentiment_type, session_id)
        return {
            'factions': factions,
            'messages': messages
        }

    def get_key_figures(self, session_id):
        factions = self.get_factions()
        sentiments = []
        highest_sentiment = None
        lowest_sentiment = None
        median = None
        sentiment_lower_quartile = None
        sentiment_upper_quartile = None

        for faction in factions:
            for other in factions:
                faction_name = faction['name']
                other_name = other['name']
                if faction_name is not other_name:
                    message = self.get_message(faction_name, other_name, "NEUTRAL", session_id)
                    if message['count'] > 0:
                        sentiments.append(message['sentiment'])

        if len(sentiments) > 0:
            highest_sentiment = sorted(sentiments, reverse=True)
            del highest_sentiment[1:]
            lowest_sentiment = sorted(sentiments)
            del lowest_sentiment[1:]
            sentiments = sorted(sentiments)
            median = np.median(sentiments)
            sentiment_lower_quartile = np.quantile(sentiments, 0.25)
            sentiment_upper_quartile = np.quantile(sentiments, 0.75)

        return {
            'lowest_sentiment': lowest_sentiment[0],
            'highest_sentiment': highest_sentiment[0],
            'sentiment_median': median,
            'sentiment_lower_quartile': sentiment_lower_quartile,
            'sentiment_upper_quartile': sentiment_upper_quartile
        }

    def get_messages(self, sentiment_type="NEUTRAL", session_id=None):
        where = self.get_where_clause(sentiment_type, session_id)
        with self.driver.session() as session:
            query = 'MATCH p=(sender:{0})-[r:{1}]->(recipient:{0}) ' \
                    '{2}' \
                    'with sender, recipient, sum(r.weight) as weightsum, ' \
                    'collect(distinct r.sessionId) as sessionList, ' \
                    'collect(r) as rlist unwind rlist as r ' \
                    'RETURN sender.factionId as sender, recipient.factionId as recipient, ' \
                    'count(r) as count, sum((r.weight/weightsum)*r.polarity) as sentiment, sessionList as sessionIds' \
                .format(NODE_FACTION, REL_COMMENTED, where)

            return session.run(query).data()

    def get_factions_ranked(self, sentiment_type, session_id=None):
        factions = self.get_factions()
        messages = self.get_messages(sentiment_type, session_id)
        ranked = calculate_pagerank_eigenvector(factions, messages, field_name='factionId')
        return sorted(ranked, key=lambda x: x['rank'], reverse=True)

    def get_where_clause(self, sentiment_type="NEUTRAL", session_id=None):
        where = 'WHERE NOT sender.factionId = recipient.factionId '

        if session_id is not None:
            where = where + " AND r.sessionId={0} ".format(session_id)

        if sentiment_type == 'POSITIVE':
            where = where + " AND r.polarity > 0 "

        if sentiment_type == 'NEGATIVE':
            where = where + " AND r.polarity < 0 "

        return where


def setup_group5_db():
    database_url = getenv('GROUP5_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP5_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP5_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group5Database(database_url, database_user, database_password)
    return db
