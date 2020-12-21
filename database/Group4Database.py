from os import getenv

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
    def get_persons(self, sentiment_type="NEUTRAL", session_id=None):
        with self.driver.session() as session:

            where = ""
            if sentiment_type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if sentiment_type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            if session_id is not None:
                if len(where) is 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "ses.sessionId = {0}".format(session_id)

            query = "MATCH (p:{0})-[r:{1}]->(f:{2}) " \
                    "MATCH (p)-[c:{3}|{4}]-(m:{5})-[d:{6}]->(ses:{7})" \
                    "{8}" \
                    "RETURN DISTINCT p,f" \
                    .format(NODE_PERSON, REL_MEMBER, NODE_FACTION, REL_SENDER, REL_RECEIVER, NODE_COMMENTARY,
                            REL_SESSION, NODE_SESSION, where)

            print(query)

            persons = session.run(query)
            arr = []
            for person in persons:
                arr.append({
                    'name': person.data()['p']['name'],
                    'speakerId': person.data()['p']['speakerId'],
                    'role': person.data()['p']['role'],
                    'faction': person.data()['f']['name']
                })
            return arr

    def get_messages(self, sentiment_type="NEUTRAL", session_id=None):
        with self.driver.session() as session:
            where = ""
            if sentiment_type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if sentiment_type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            if session_id is not None:
                if len(where) is 0:
                    where = "WHERE "
                else:
                    where = where + " AND "
                where = where + "ses.sessionId = {0}".format(session_id)

            query = "MATCH (a)-[s:{0}]->(m:{1})-[r:{2}]->(b) " \
                    "MATCH (m)-[d:{4}]->(ses:{5})" \
                    "{3}" \
                    "RETURN m.sentiment AS sentiment, m.dateString as date, ses.sessionId as sessionId, " \
                    "a.speakerId AS sender, b.speakerId AS recipient"\
                .format(REL_SENDER, NODE_COMMENTARY, REL_RECEIVER, where, REL_SESSION, NODE_SESSION)

            print(query)

            messages = session.run(query)
            return messages.data()

    def get_graph(self, sentiment_type="NEUTRAL", session_id=None):
        return {
            'persons': self.get_persons(sentiment_type, session_id),
            'messages': aggregate_messages(self.get_messages(sentiment_type, session_id))
        }

    def get_factions(self):
        with self.driver.session() as session:
            query = "MATCH (f:{}) return f.factionId as factionId, f.name as name".format(NODE_FACTION)
            return session.run(query).data()

    def get_persons_ranked(self, sentiment_type, session_id=None):
        persons = self.get_persons()
        messages = self.get_messages(sentiment_type, session_id)
        ranked = calculate_pagerank_eigenvector(persons, aggregate_messages(messages))
        return sorted(ranked, key=lambda x: x['rank'], reverse=True)

    def get_sessions(self):
        with self.driver.session() as session:
            query = "MATCH (s:{0}) return s.sessionId as sessionId, s.legislative_period as legislativePeriod, " \
                    "s.startDateTime as startDateTime, s.endDateTime as endDateTime".format(NODE_SESSION)
            sessions = session.run(query).data()
            return sessions

    def get_session(self, session_id):
        with self.driver.session() as session:
            query = "MATCH (s:{0}) WHERE s.sessionId = {1} " \
                    "return s.sessionId as sessionId, s.legislative_period as legislativePeriod, " \
                    "s.startDateTime as startDateTime, s.endDateTime as endDateTime"\
                .format(NODE_SESSION, session_id)
            s = session.run(query).data()[0]
            return s


def setup_group4_db():
    database_url = getenv('GROUP4_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('GROUP4_DATABASE_USER', 'neo4j')
    database_password = getenv('GROUP4_DATABASE_PASSWORD', 'graphenauswertung')

    db = Group4Database(database_url, database_user, database_password)
    return db
