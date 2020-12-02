from neo4j import GraphDatabase
import numpy as np
from pagerank import pagerank, aggregate_messages


class Database:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    def clear(self):
        with self.driver.session() as session:
            session.write_transaction(self._clear)

    def seed(self):
        with self.driver.session() as session:
            session.write_transaction(self._seed)

    def getPersons(self):
        with self.driver.session() as session:
            persons = session.run("MATCH (n:Person) RETURN n.vorname, n.nachname, n.rednerId")
            arr = np.array([])
            for person in persons:
                arr = np.append(arr, {
                    'vorname': person.data()['n.vorname'],
                    'nachname': person.data()['n.nachname'],
                    "rednerId": person.data()['n.rednerId']
                })
            return arr.tolist()

    def getPersonsWithRank(self, type):
        persons = self.getPersons()
        messages = self.getMessages(type)
        ranked = pagerank(persons, aggregate_messages(messages))
        return ranked.tolist()

    def getMessages(self, type):
        with self.driver.session() as session:
            query = "MATCH (a)-[s:INTERAGIERT_DURCH]->(m:Kommentar)-[r:INTERAGIERT_MIT]->(b) RETURN m.sentiment AS sentiment, a.rednerId AS sender, b.rednerId AS recipient"
            if type == 'POSITIVE':
                query = "MATCH (a)-[s:INTERAGIERT_DURCH]->(m:Kommentar)-[r:INTERAGIERT_MIT]->(b) WHERE m.sentiment > 0 RETURN m.sentiment AS sentiment, a.rednerId AS sender, b.rednerId AS recipient"
            if type == 'NEGATIVE':
                query = "MATCH (a)-[s:INTERAGIERT_DURCH]->(m:Kommentar)-[r:INTERAGIERT_MIT]->(b) WHERE m.sentiment < 0 RETURN m.sentiment AS sentiment, a.rednerId AS sender, b.rednerId AS recipient"

            messages = session.run(query)
            return messages.data()

    def getPersonsWithMessages(self, type):
        with self.driver.session() as session:
            persons = self.getPersons()
            arr = np.array([])
            for person in persons:
                p = {
                    "name": person,
                    "ingoingMessages": self.getIngoingMessages(person)
                }
                arr = np.append(arr, p)
            return arr.tolist()

    def getIngoingMessages(self, person):
        with self.driver.session() as session:
            messages = session.run(
                "MATCH (a)-[s]->(m:Kommentar)-[r]->(b) WHERE b.rednerId='" + person + "' RETURN m.sentiment AS sentiment, a.rednerId AS rednerId")
            return messages.data()

    def getAvgSentiment(self):
        with self.driver.session() as session:
            query = "MATCH (m:Kommentar) RETURN m.sentiment"
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
        Database._clear(tx)
        Database._seedPersons(tx)

    @staticmethod
    def _seedPersons(tx):
        fractions = [
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
                'rednerId': 'p1',
                'vorname': 'Angela',
                'nachname': 'Merkel',
                'nameszusatz': '',
                'titel': '',
                'bdland': ''
            },
            {
                'rednerId': 'p2',
                'vorname': 'Jens',
                'nachname': 'Spahn',
                'nameszusatz': '',
                'titel': '',
                'bdland': ''
            },
            {
                'rednerId': 'p3',
                'vorname': 'Heiko',
                'nachname': 'Maas',
                'nameszusatz': '',
                'titel': '',
                'bdland': ''
            },
            {
                'rednerId': 'p4',
                'vorname': 'Weidel',
                'nachname': 'Alice',
                'nameszusatz': '',
                'titel': '',
                'bdland': ''
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

        query = query + "CREATE (w1:Wahlperiode{number:19,startDate: date('2019-06-01'),endDate: date('2020-12-31')})\n"

        query = query + "CREATE (si1:Sitzung{startDateTime: datetime('2019-06-01T18:40:32.142+0100'), endDateTime: datetime('2019-06-01T20:40:32.142+0100')})\n"
        query = query + "CREATE (si1)-[wa1:WAEHREND]->(w1)\n"

        query = query + "CREATE (si2:Sitzung{startDateTime: datetime('2019-05-01T18:40:32.142+0100'), endDateTime: datetime('2019-05-01T20:40:32.142+0100')})\n"
        query = query + "CREATE (si2)-[wa2:WAEHREND]->(w1)\n"



        fcnt = 0
        for fraction in fractions:
            query = query + "CREATE (f" + str(fcnt) + ":Fraktion{name:'" + fraction['name'] + "',beschreibung:'" + fraction['beschreibung'] + "'})\n"
            fcnt = fcnt + 1

        for person in persons:
            query = query + "CREATE (" + person['rednerId']+":Person{vorname:'" + person['vorname'] + "', nachname: '" + person['nachname'] +"', rednerId:'" + person['rednerId'] + "'}) \n"


        query = query + "CREATE(p1)-[fr1:mitglied_von]->(f0)\n"
        query = query + "CREATE(p2)-[fr2:mitglied_von]->(f0)\n"
        query = query + "CREATE(p3)-[fr3:mitglied_von]->(f1)\n"
        query = query + "CREATE(p4)-[fr4:mitglied_von]->(f2)\n"


        cnt = 0
        for message in messages:
            query = query + "CREATE(m" + str(cnt) + ": Kommentar{sentiment: " + str(message['sentiment']) + ",beschreibung:'',art:'kommentar',date: date('2020-11-28')}) \n"
            query = query + "CREATE(" + message['from'] + ") - [s" + str(cnt) + ": INTERAGIERT_DURCH] -> (m" + str(cnt) + ") \n "
            query = query + "CREATE(m" + str(cnt) + ") - [r" + str(cnt) + ": INTERAGIERT_MIT] -> (" + message['to'] + ") \n"
            query = query + "CREATE(m" + str(cnt) + ") - [e" + str(cnt) + ":ERFOLGT_IN] -> (si1) \n"
            cnt = cnt + 1

        tx.run(query)

    @staticmethod
    def _clear(tx):
        return tx.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]
