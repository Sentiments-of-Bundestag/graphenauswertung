import numpy as np


def aggregate_messages(messages):
    result = []
    for message in messages:
        existing_entries = [x for x in result if (x['sender'] == message['sender'] and x['recipient'] == message['recipient'])]
        if len(existing_entries) > 0:
            entry = existing_entries[0]
            count = entry['count'] + 1
            sentiment = entry['sentiment'] + message['sentiment']
            entry['count'] = count
            entry['sentiment'] = sentiment

        else:
            result.append({'sender': message['sender'], 'recipient': message['recipient'], 'count': 1, 'sentiment': message['sentiment']})

    return result


def pagerank(persons, messages):
    result = np.array([])
    start_value = 1 / len(persons)

    max_iterations = 100
    iteration = 0

    # init
    i = 0
    while i < len(persons):
        result = np.append(result, {'vorname': persons[i]['vorname'], 'nachname': persons[i]['nachname'],
                                    'rednerId': persons[i]['rednerId'], 'rank': start_value})
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
        if message['recipient'] == node['rednerId']:
            nodes_pointing_to_node = np.append(nodes_pointing_to_node, message['sender'])
            sender = [s for s in persons if s['rednerId'] == message['sender']][0]
            sum_of_pointing_prs = sum_of_pointing_prs + sender['rank']

    pr = ((1 - d) / n) + d * sum_of_pointing_prs
    return pr
