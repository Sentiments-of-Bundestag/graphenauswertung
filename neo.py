from neo4j import GraphDatabase
import numpy as np
from pagerank import pagerank


class HelloWorldExample:

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
        name = person.data()['n.name']
        p = {
          "name": name,
          "ingoingMessages": self.getIngoingMessages(name)
        }
        arr = np.append(arr, p)
      pagerank(arr)
      return arr.tolist()

  def getIngoingMessages(self, person):
    with self.driver.session() as session:
      messages = session.run("MATCH (a)-[r]->(b) WHERE b.name='" + person + "' RETURN a.name AS sender, r.sentiment AS sentiment")
      return messages.data()


  def getAvgSentiment(self):
    with self.driver.session() as session:
      query = "MATCH p =()-[r]->(b) RETURN r.sentiment"
      messages= session.run(query)
      avg = 0
      cnt = 0
      for message in messages:
        sentiment = message.data()['r.sentiment']
        print(sentiment)
        avg = avg + sentiment
        cnt = cnt + 1
      avg = avg / cnt
      return avg


  @staticmethod
  def _seed(tx):
    HelloWorldExample._clear(tx)
    HelloWorldExample._seedPersons(tx)


  @staticmethod
  def _seedPersons(tx):
    tx.run("""
    CREATE (merkel:Person{name:'Angela Merkel'}), (spahn:Person{name:'Jens Spahn'}), (weidel:Person{name:'Alice Weidel'}), (maas:Person{name:'Heiko Maas'})
    CREATE (merkel)-[r1:Message{sentiment:0.8}]->(spahn)
    CREATE (merkel)-[r2:Message{sentiment:0.5}]->(spahn)
    CREATE (merkel)-[r3:Message{sentiment:0.9}]->(spahn)
    CREATE (spahn)-[r4:Message{sentiment:-0.3}]->(weidel)
    CREATE (weidel)-[r5:Message{sentiment:-0.9}]->(merkel)
    CREATE (weidel)-[r6:Message{sentiment:-0.7}]->(spahn)
    CREATE (maas)-[r7:Message{sentiment:0.2}]->(merkel)
    CREATE (merkel)-[r8:Message{sentiment:0.5}]->(maas)
    CREATE (weidel)-[r9:Message{sentiment:-0.2}]->(maas)
    CREATE (spahn)-[r10:Message{sentiment:0.1}]->(maas)
    """)

  @staticmethod
  def _clear(tx):
    return tx.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

  @staticmethod
  def _create_and_return_greeting(tx, message):
    result = tx.run("CREATE (a:Greeting) "
                    "SET a.message = $message "
                    "RETURN a.message + ', from node ' + id(a)", message=message)
    return result.single()[0]