from neo4j import GraphDatabase
import numpy as np
from pagerank import pagerank


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
            persons = session.run("MATCH (n:Person) RETURN n.name")
            arr = np.array([])
            for person in persons:
                arr = np.append(arr, person.data()['n.name'])
            return arr.tolist()

    def getPersonsWithRank(self, type):
        persons = self.getPersons()
        messages = self.getMessages(type)
        ranked = pagerank(persons, messages)
        return ranked.tolist()

    def getMessages(self, type):
        with self.driver.session() as session:
            query = "MATCH (a)-[s]->(m:Message)-[r]->(b) RETURN m.sentiment AS sentiment, a.name AS sender, b.name AS recipient"
            if type == 'POSITIVE':
                query = "MATCH (a)-[s]->(m:Message)-[r]->(b) WHERE m.sentiment > 0 RETURN m.sentiment AS sentiment, a.name AS sender, b.name AS recipient"
            if type == 'NEGATIVE':
                query = "MATCH (a)-[s]->(m:Message)-[r]->(b) WHERE m.sentiment < 0 RETURN m.sentiment AS sentiment, a.name AS sender, b.name AS recipient"

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
                "MATCH (a)-[s]->(m:Message)-[r]->(b) WHERE b.name='" + person + "' RETURN m.sentiment AS sentiment, a.name AS name")
            return messages.data()

    def getAvgSentiment(self):
        with self.driver.session() as session:
            query = "MATCH (m:Message) RETURN m.sentiment"
            messages = session.run(query)
            avg = 0
            cnt = 0
            for message in messages:
                sentiment = message.data()['m.sentiment']
                print(sentiment)
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
        persons = [
            {
                'name': 'Angela Merkel',
                'id': 'merkel'
            },
            {
                'name': 'Jens Spahn',
                'id': 'spahn'
            },
            {
                'name': 'Heiko Maas',
                'id': 'maas'
            },
            {
                'name': 'Alice Weidel',
                'id': 'weidel'
            }
        ]
        messages = [
            {
                'from': 'merkel',
                'to': 'spahn',
                'sentiment': 0.8
            },
            {
                'from': 'merkel',
                'to': 'spahn',
                'sentiment': 0.5
            },
            {
                'from': 'merkel',
                'to': 'spahn',
                'sentiment': 0.9
            },
            {
                'from': 'spahn',
                'to': 'weidel',
                'sentiment': -0.3
            },
            {
                'from': 'weidel',
                'to': 'merkel',
                'sentiment': -0.9
            },
            {
                'from': 'weidel',
                'to': 'spahn',
                'sentiment': -0.7
            },
            {
                'from': 'maas',
                'to': 'merkel',
                'sentiment': 0.2
            },
            {
                'from': 'merkel',
                'to': 'maas',
                'sentiment': 0.5
            },
            {
                'from': 'weidel',
                'to': 'maas',
                'sentiment': -0.2
            },
            {
                'from': 'spahn',
                'to': 'maas',
                'sentiment': 0.1
            }
        ]
        query = ""
        for person in persons:
            query = query + "CREATE (" + person['id']+":Person{name:'" + person['name'] + "'}) \n"

        cnt = 0
        for message in messages:
            query = query + "CREATE(m" + str(cnt) + ": Message{sentiment: " + str(message['sentiment']) + "}) \n"
            query = query + "CREATE(" + message['from'] + ") - [s" + str(cnt) + ": Sends] -> (m" + str(cnt) + ") \n "
            query = query + "CREATE(m" + str(cnt) + ") - [r" + str(cnt) + ": Receives] -> (" + message['to'] + ") \n"
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
