import numpy as np


def pagerank(persons, messages):
    result = np.array([])
    start_value = 1 / len(persons)

    max_iterations = 100
    iteration = 0

    # init
    i = 0
    while i < len(persons):
        result = np.append(result, {'name': persons[i], 'rank': start_value})
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
        if message['recipient'] == node['name'] and not np.isin(message['sender'], nodes_pointing_to_node):
            nodes_pointing_to_node = np.append(nodes_pointing_to_node, message['sender'])
            sender = [s for s in persons if s['name'] == message['sender']][0]
            sum_of_pointing_prs = sum_of_pointing_prs + sender['rank']

    pr = ((1 - d) / n) + d * sum_of_pointing_prs
    return pr

