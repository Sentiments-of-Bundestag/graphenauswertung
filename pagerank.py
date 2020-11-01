import numpy as np

def pagerank(nodes):
    result = np.copy(nodes)
    start_value = 1 / len(result)

    max_iterations = 100
    iteration = 0

    # init
    for node in result:
        node['rank'] = start_value

    # iteration
    while iteration < max_iterations:
        for node in result:
            node['rank'] = pagerank_step(node, result)
        iteration = iteration + 1

    return result

def pagerank_step(node, nodes):
    n = len(nodes)
    d = 0.5
    sum_of_pointing_prs = 0

    nodes_pointing_to_node = np.array([])
    for message in node['ingoingMessages']:
        if not np.isin(message['sender'], nodes_pointing_to_node):
            nodes_pointing_to_node = np.append(nodes_pointing_to_node, message['sender'])
            for sender in nodes:
                if sender['name'] == message['sender']:
                    sum_of_pointing_prs = sum_of_pointing_prs + sender['rank']
        #if (n['name'] is not node['name']):
        #    for message in n['ingoingMessages']:
        #        print(message)
        #    sum_of_pointing_prs = sum_of_pointing_prs + n['rank']

    print(node['name'])
    print(nodes_pointing_to_node)
    print(sum_of_pointing_prs)
    print('#####')

    pr = ((1-d) / n) + d * sum_of_pointing_prs
    return pr