import numpy as np
from pagerank import calculate_pagerank_eigenvector, aggregate_messages
from database.Database import Database
from os import getenv

NODE_PERSON = 'Person'
NODE_KOMMENTAR = 'Commentary'
NODE_SITZUNG = 'ParliamentSession'
NODE_WAHLPERIODE = 'Wahlperiode'
NODE_FACTION = 'Faction'
REL_WAEHREND = 'WAHREND'
REL_SEND = 'SENDER'
REL_RECEIVE = 'RECEIVER'
REL_ERFOLGT = 'SESSION'
REL_MITGLIED = 'MEMBER'


class MockDatabase(Database):
    def clear(self):
        with self.driver.session() as session:
            session.write_transaction(self._clear)

    def seed(self):
        with self.driver.session() as session:
            session.write_transaction(self._seed)

    def get_persons(self):
        with self.driver.session() as session:
            persons = session.run("MATCH (n:" + NODE_PERSON + ") RETURN n.name, n.speakerId, n.role")
            arr = np.array([])
            for person in persons:
                arr = np.append(arr, {
                    'name': person.data()['n.name'],
                    'speakerId': person.data()['n.speakerId'],
                    "role": person.data()['n.role']
                })
            return arr.tolist()

    def get_persons_with_rank(self, type):
        persons = self.get_persons()
        messages = self.get_messages(type)
        ranked = calculate_pagerank_eigenvector(persons, aggregate_messages(messages))
        return ranked

    def get_messages(self, type):
        with self.driver.session() as session:
            where = ""
            if type == "POSITIVE":
                where = "WHERE m.sentiment > 0"
            if type == "NEGATIVE":
                where = "WHERE m.sentiment < 0"

            query = "MATCH (a)-[s:" + REL_SEND + "]->(m:" + NODE_KOMMENTAR + ")-[r:" + REL_RECEIVE + "]->(b) " \
                    + where + " RETURN m.sentiment AS sentiment, a.speakerId AS sender, b.speakerId AS recipient"

            messages = session.run(query)
            return messages.data()

    def get_avg_sentiment(self):
        with self.driver.session() as session:
            query = "MATCH (m:" + NODE_KOMMENTAR + ") RETURN m.sentiment"
            messages = session.run(query)
            avg = 0
            cnt = 0
            for message in messages:
                sentiment = message.data()['m.sentiment']
                avg = avg + sentiment
                cnt = cnt + 1
            if (cnt > 0):
                avg = avg / cnt
            return avg

    @staticmethod
    def _seed(tx):
        MockDatabase._clear(tx)
        MockDatabase._seedPersons(tx)

    @staticmethod
    def _seedPersons(tx):
        factions = [
            {
                'name': 'CDU/CSU',
                'beschreibung': ''
            },
            {
                'name': 'SPD',
                'beschreibung': ''
            },
            {
                'name': 'AFD',
                'beschreibung': ''
            }
        ]
        persons = [
            {
                'speakerId': 'p1',
                'name': 'Angela Merkel',
                'role': ''
            },
            {
                'speakerId': 'p2',
                'name': 'Jens Spahn',
                'role': ''
            },
            {
                'speakerId': 'p3',
                'name': 'Heiko Maas',
                'role': ''
            },
            {
                'speakerId': 'p4',
                'name': 'Alice Weidel',
                'role': ''
            }
        ]
        messages = [
            {
                'from': 'p1',
                'to': 'p2',
                'sentiment': 0.8
            },
            {
                'from': 'p1',
                'to': 'p2',
                'sentiment': 0.5
            },
            {
                'from': 'p1',
                'to': 'p2',
                'sentiment': 0.9
            },
            {
                'from': 'p2',
                'to': 'p4',
                'sentiment': -0.3
            },
            {
                'from': 'p4',
                'to': 'p1',
                'sentiment': -0.9
            },
            {
                'from': 'p4',
                'to': 'p2',
                'sentiment': -0.7
            },
            {
                'from': 'p3',
                'to': 'p1',
                'sentiment': 0.2
            },
            {
                'from': 'p1',
                'to': 'p3',
                'sentiment': 0.5
            },
            {
                'from': 'p4',
                'to': 'p3',
                'sentiment': -0.2
            },
            {
                'from': 'p2',
                'to': 'p3',
                'sentiment': 0.1
            }
        ]
        query = ""

        query = query + "CREATE (w1:" + NODE_WAHLPERIODE + "{number:19,startDate: date('2019-06-01'),endDate: date('2020-12-31')})\n"

        query = query + "CREATE (si1:Sitzung{startDateTime: datetime('2019-06-01T18:40:32.142+0100'), endDateTime: datetime('2019-06-01T20:40:32.142+0100')})\n"
        query = query + "CREATE (si1)-[wa1:" + REL_WAEHREND + "]->(w1)\n"

        query = query + "CREATE (si2:Sitzung{startDateTime: datetime('2019-05-01T18:40:32.142+0100'), endDateTime: datetime('2019-05-01T20:40:32.142+0100')})\n"
        query = query + "CREATE (si2)-[wa2:" + REL_WAEHREND + "]->(w1)\n"

        fcnt = 0
        for fraction in factions:
            query = query + "CREATE (f" + str(fcnt) + ":" + NODE_FACTION + "{name:'" + fraction[
                'name'] + "',beschreibung:'" + \
                    fraction['beschreibung'] + "'})\n"
            fcnt = fcnt + 1

        for person in persons:
            query = query + "CREATE (" + person['speakerId'] + ":" + NODE_PERSON + "{name:'" + person[
                'name'] + "', role: '" + person['role'] + "', speakerId:'" + person['speakerId'] + "'}) \n"

        query = query + "CREATE(p1)-[fr1:" + REL_MITGLIED + "]->(f0)\n"
        query = query + "CREATE(p2)-[fr2:" + REL_MITGLIED + "]->(f0)\n"
        query = query + "CREATE(p3)-[fr3:" + REL_MITGLIED + "]->(f1)\n"
        query = query + "CREATE(p4)-[fr4:" + REL_MITGLIED + "]->(f2)\n"

        cnt = 0
        for message in messages:
            _cnt = str(cnt)
            query = query + "CREATE(m" + _cnt + ": " + NODE_KOMMENTAR + "{sentiment: " + str(
                message['sentiment']) + ",beschreibung:'',art:'kommentar',date: date('2020-11-28')}) \n"
            query = query + "CREATE(" + message['from'] + ") - [s" + _cnt + ": " + REL_SEND + "] -> (m" + _cnt + ") \n "
            query = query + "CREATE(m" + _cnt + ") - [r" + _cnt + ": " + REL_RECEIVE + "] -> (" + message['to'] + ") \n"
            query = query + "CREATE(m" + _cnt + ") - [e" + _cnt + ":" + REL_ERFOLGT + "] -> (si1) \n"
            cnt = cnt + 1

        tx.run(query)

    @staticmethod
    def _clear(tx):
        return tx.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")


def setup_mock_db():
    database_url = getenv('MOCK_DATABASE_URL', 'bolt://localhost:7687')
    database_user = getenv('MOCK_DATABASE_USER', 'neo4j')
    database_password = getenv('MOCK_DATABASE_PASSWORD', 'graphenauswertung')

    db = MockDatabase(database_url, database_user, database_password)
    db.seed()
    return db
