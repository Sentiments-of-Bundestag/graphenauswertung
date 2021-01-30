import numpy as np


def aggregate_messages(messages):
    existing_entries = {}
    for message in messages:
        message_key = message['sender']+':'+message['recipient']
        try:
            existing_entry = existing_entries[message_key]
            count = existing_entry['count'] + 1
            sentiment = existing_entry['sentiment'] + message['sentiment']
            existing_entry['count'] = count
            existing_entry['sentiment'] = sentiment

        except KeyError:
            new_entry = {'sender': message['sender'], 'recipient': message['recipient'], 'count': 1,
                         'sentiment': message['sentiment']}
            existing_entries[message_key] = new_entry

    result = list(existing_entries.values())

    for m in result:
        m['sentiment'] = m['sentiment'] / m['count']

    return result


def calculate_pagerank_eigenvector(persons, messages, field_name='speakerId', reverse=False, max_iterations=100, d=0.85):
    person_ids = sorted([person[field_name] for person in persons])
    n = len(person_ids)
    matrix = np.zeros((n, n))

    for person in person_ids:
        outgoing_messages = [message for message in messages if message['recipient'] == person] if reverse \
            else [message for message in messages if message['sender'] == person]

        for outgoing_message in outgoing_messages:
            j = person_ids.index(person)
            i = person_ids.index(outgoing_message['sender']) if reverse else person_ids.index(outgoing_message['recipient'])
            matrix[i, j] = 1 / len(outgoing_messages)

        if len(outgoing_messages) == 0:
            for recipient in person_ids:
                j = person_ids.index(person)
                i = person_ids.index(recipient)
                matrix[i, j] = 1 / n

    matrix = d * matrix + (1 - d) / n
    pagerank = np.full(n, 1 / n)

    for i in range(0, max_iterations):
        old_pagerank = pagerank
        pagerank = np.dot(matrix, pagerank)
        if np.array_equal(pagerank, old_pagerank):
            break

    persons = sorted(persons, key=lambda entry: entry[field_name])
    for rank, person in zip(pagerank, persons):
        person['rank'] = rank

    return persons


def calculate_pagerank(persons, messages):
    result = np.array([])
    start_value = 1 / len(persons)

    max_iterations = 100
    iteration = 0

    # init
    i = 0
    while i < len(persons):
        result = np.append(result, {'name': persons[i]['name'],
                                    'speakerId': persons[i]['speakerId'], 'rank': start_value})
        i = i + 1

    # iteration
    while iteration < max_iterations:
        for node in result:
            node['rank'] = pagerank_step(node, result, messages)
        iteration = iteration + 1

    return result


def pagerank_step(node, persons, messages):
    n = len(persons)
    d = 0.3
    sum_of_pointing_prs = 0

    nodes_pointing_to_node = np.array([])
    for message in messages:
        if message['recipient'] == node['speakerId']:
            nodes_pointing_to_node = np.append(nodes_pointing_to_node, message['sender'])
            sender = [s for s in persons if s['speakerId'] == message['sender']][0]
            sum_of_pointing_prs = sum_of_pointing_prs + sender['rank']

    pr = ((1 - d) / n) + d * sum_of_pointing_prs
    return pr
