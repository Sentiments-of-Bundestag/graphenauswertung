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
      messages = session.run("MATCH (a)-[s]->(m:Message)-[r]->(b) WHERE b.name='" + person + "' RETURN m.sentiment AS sentiment, a.name AS name")
      return messages.data()


  def getAvgSentiment(self):
    with self.driver.session() as session:
      query = "MATCH (m:Message) RETURN m.sentiment"
      messages= session.run(query)
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
        'name': 'Angela Merkel'
      }
    ]
    tx.run("""
    CREATE (merkel:Person{name:'Angela Merkel'}), (spahn:Person{name:'Jens Spahn'}), (weidel:Person{name:'Alice Weidel'}), (maas:Person{name:'Heiko Maas'})
    CREATE (n1:Message{sentiment:0.8})
    CREATE (merkel)-[s1:Sends]->(n1)
    CREATE (n1)-[r1:Receives]->(spahn)
    
    CREATE (n2:Message{sentiment:0.5})
    CREATE (merkel)-[s2:Sends]->(n2)
    CREATE (n2)-[r2:Receives]->(spahn)
      
    CREATE (n3:Message{sentiment:0.9})
    CREATE (merkel)-[s3:Sends]->(n3)
    CREATE (n3)-[r3:Receives]->(spahn)
    
    CREATE (n4:Message{sentiment:-0.3})
    CREATE (spahn)-[s4:Sends]->(n4)
    CREATE (n4)-[r4:Receives]->(weidel)
    
    CREATE (n5:Message{sentiment:-0.9})
    CREATE (weidel)-[s5:Sends]->(n5)
    CREATE (n5)-[r5:Receives]->(merkel)
    
    CREATE (n6:Message{sentiment:-0.7})
    CREATE (weidel)-[s6:Sends]->(n6)
    CREATE (n6)-[r6:Receives]->(spahn)
    
    CREATE (n7:Message{sentiment:0.2})
    CREATE (maas)-[s7:Sends]->(n7)
    CREATE (n7)-[r7:Receives]->(merkel)
    
    CREATE (n8:Message{sentiment:0.5})
    CREATE (merkel)-[s8:Sends]->(n8)
    CREATE (n8)-[r8:Receives]->(maas)
    
    CREATE (n9:Message{sentiment:-0.2})
    CREATE (weidel)-[s9:Sends]->(n9)
    CREATE (n9)-[r9:Sends]->(maas)
    
    CREATE (n10:Message{sentiment:0.1})
    CREATE (spahn)-[s10:Sends]->(n10)
    CREATE (n10)-[r10:Receives]->(maas)
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