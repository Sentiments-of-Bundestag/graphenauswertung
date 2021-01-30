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
    def get_persons(self, sentiment_type="NEUTRAL", session_id=None, person_id=None):
        with self.driver.session() as session:

            where = ""
            if sentiment_type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if sentiment_type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            session_match = "MATCH (p)-[c:{0}|{1}]-(m:{2})-[d:{3}]->(ses:{4})" \
                .format(REL_SENDER, REL_RECEIVER, NODE_COMMENTARY, REL_SESSION, NODE_SESSION)
            if session_id is not None:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "ses.sessionId = {0}".format(session_id)

            if person_id is not None:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "p.speakerId = '{0}'".format(person_id)

            query = "MATCH (p:{0})" \
                    "OPTIONAL MATCH (p)-[r:{1}]->(f:{2})" \
                    "{3}" \
                    "{4}" \
                    "RETURN DISTINCT p.name as name, p.speakerId as speakerId, p.role as role, " \
                    "f.name as faction, f.factionId as factionId, ses.sessionId as sessionId" \
                .format(NODE_PERSON, REL_MEMBER, NODE_FACTION, session_match, where)

            persons = session.run(query)
            arr = []
            for person in persons:
                existing_entries = [x for x in arr if(x['speakerId'] == person['speakerId'])]
                if len(existing_entries) > 0:
                    entry = existing_entries[0]
                    if person['sessionId'] not in entry['sessionIds']:
                        entry['sessionIds'].append(person['sessionId'])
                else:
                    arr.append({
                        'name': person.data()['name'],
                        'speakerId': person.data()['speakerId'],
                        'role': person.data()['role'],
                        'faction': person.data()['faction'],
                        'factionId': person.data()['factionId'],
                        'sessionIds': [person['sessionId']]
                    })
            return arr

    def get_messages(self, sentiment_type="NEUTRAL", session_id=None, person_id=None, exclude_applause=False):
        with self.driver.session() as session:
            where = ""
            if sentiment_type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if sentiment_type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            if session_id is not None:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "ses.sessionId = {0}".format(session_id)

            if person_id is not None:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "a.speakerId = '{0}' OR b.speakerId = '{0}'".format(person_id)

            if exclude_applause is True:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "COALESCE(m.applause, false) <> true"

            query = "MATCH (a)-[s:{0}]->(m:{1})-[r:{2}]->(b) " \
                    "MATCH (m)-[d:{4}]->(ses:{5}) " \
                    "{3} " \
                    "RETURN m.sentiment AS sentiment, ses.sessionId as sessionId, " \
                    "a.speakerId AS sender, b.speakerId AS recipient" \
                .format(REL_SENDER, NODE_COMMENTARY, REL_RECEIVER, where, REL_SESSION, NODE_SESSION)

            messages = session.run(query)
            return messages.data()

    def get_graph(self, sentiment_type="NEUTRAL", session_id=None, person_id=None, exclude_applause=False):
        return {
            'persons': self.get_persons(sentiment_type, session_id, person_id),
            'messages': aggregate_messages(self.get_messages(sentiment_type, session_id, person_id, exclude_applause))
        }

    def get_factions(self):
        with self.driver.session() as session:
            query = "MATCH (f:{}) return f.factionId as factionId, f.name as name".format(NODE_FACTION)
            return session.run(query).data()

    def get_persons_ranked(self, sentiment_type, session_id=None, reverse=None, exclude_applause=False):
        persons = self.get_persons()
        messages = self.get_messages(sentiment_type, session_id, exclude_applause)
        ranked = calculate_pagerank_eigenvector(persons, aggregate_messages(messages), reverse=reverse)
        return sorted(ranked, key=lambda x: x['rank'], reverse=True)

    def get_key_figures(self, session_id=None, exclude_applause=False):
        with self.driver.session() as session:

            where = ""

            if session_id is not None:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "ses.sessionId = {0}".format(session_id)

            if exclude_applause is True:
                if len(where) == 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "COALESCE(m.applause, false) <> true"

            query = 'MATCH (c:{0})-[:{1}]->(ps:{2}) {3} RETURN c.sentiment AS sentiment' \
                    .format(NODE_COMMENTARY, REL_SESSION, NODE_SESSION, where)

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
                'lowest_sentiment': lowest_sentiment[0],
                'highest_sentiment': highest_sentiment[0],
                'sentiment_median': median,
                'sentiment_lower_quartile': sentiment_lower_quartile,
                'sentiment_upper_quartile': sentiment_upper_quartile
            }

    def get_sessions(self):
        with self.driver.session() as session:
            query = "MATCH (s:{0}) RETURN s.sessionId as sessionId, s.legislative_period as legislativePeriod, " \
                    "s.startDateTime as startDateTime, s.endDateTime as endDateTime ORDER BY s.startDateTime"\
                .format(NODE_SESSION)
            sessions = session.run(query).data()
            return sessions

    def get_session(self, session_id):
        with self.driver.session() as session:
            query = "MATCH (s:{0}) WHERE s.sessionId = {1} " \
                    "return s.sessionId as sessionId, s.legislative_period as legislativePeriod, " \
                    "s.startDateTime as startDateTime, s.endDateTime as endDateTime" \
                .format(NODE_SESSION, session_id)
            s = session.run(query).data()[0]
            return s



def setup_group4_db():
    database_url = getenv('GROUP4_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP4_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP4_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group4Database(database_url, database_user, database_password)
    return db
