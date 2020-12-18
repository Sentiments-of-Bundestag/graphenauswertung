from os import getenv
import numpy as np

from database.Database import Database
from pagerank import aggregate_messages, calculate_pagerank_eigenvector

NODE_PERSON = 'Person'
NODE_FACTION = 'Faction'
NODE_COMMENTARY = 'Commentary'
NODE_SESSION = 'ParliamentSession'
REL_MEMBER = 'MEMBER'
REL_SESSION = 'SESSION'
REL_RECEIVER = 'RECEIVER'
REL_SENDER = 'SENDER'


class Group4Database(Database):
    def get_persons(self):
        with self.driver.session() as session:
            persons = session.run("MATCH (p:{0})-[r:{1}]->(f:{2}) RETURN p,f"
                                  .format(NODE_PERSON, REL_MEMBER, NODE_FACTION))
            arr = []
            for person in persons:
                arr.append({
                    'name': person.data()['p']['name'],
                    'speakerId': person.data()['p']['speakerId'],
                    'role': person.data()['p']['role'],
                    'faction': person.data()['f']['name']
                })
            return arr

    def get_messages(self, sentiment_type="NEUTRAL"):
        with self.driver.session() as session:
            where = ""
            if sentiment_type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if sentiment_type == "NEGATIVE":
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

    def get_persons_ranked(self, sentiment_type):
        persons = self.get_persons()
        messages = self.get_messages(sentiment_type)
        ranked = calculate_pagerank_eigenvector(persons, aggregate_messages(messages))
        return sorted(ranked, key=lambda x: x['rank'], reverse=True)

    def get_key_figures(self, session_id):
        with self.driver.session() as session:
            if session_id is None:
                query = 'MATCH (c:{0})-[:{1}]->(ps:{2}) RETURN c.sentiment AS sentiment' \
                    .format(NODE_COMMENTARY, REL_SESSION, NODE_SESSION)
            else:
                query = 'MATCH (c:{0})-[:{1}]->(ps:{2}) WHERE ps.sessionId = {3} RETURN c.sentiment AS sentiment' \
                    .format(NODE_COMMENTARY, REL_SESSION, NODE_SESSION, session_id)
            data = session.run(query)
            data = data.data()

            sentiments = []
            highest_sentiment = None
            lowest_sentiment = None
            median = None
            sentiment_lower_quartile = None
            sentiment_upper_quartile = None

            if len(data) > 0:
                for element in data:
                    sentiments.append(element['sentiment'])
                highest_sentiment = sorted(sentiments, reverse=True)
                del highest_sentiment[1:]
                lowest_sentiment = sorted(sentiments)
                del lowest_sentiment[1:]
                sentiments = sorted(sentiments)
                median = np.median(sentiments)
                sentiment_lower_quartile = np.quantile(sentiments, 0.25)
                sentiment_upper_quartile = np.quantile(sentiments, 0.75)

            return {
                'lowest_sentiment': lowest_sentiment,
                'highest_sentiment': highest_sentiment,
                'sentiment_median': median,
                'sentiment_lower_quartile': sentiment_lower_quartile,
                'sentiment_upper_quartile': sentiment_upper_quartile
            }


def setup_group4_db():
    database_url = getenv('GROUP4_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP4_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP4_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group4Database(database_url, database_user, database_password)
    return db
