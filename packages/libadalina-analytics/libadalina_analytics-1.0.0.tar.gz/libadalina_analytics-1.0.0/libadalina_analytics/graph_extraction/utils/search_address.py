def get_node_of_address(graph, address):
    """
    Get the node of a given address in the graph.

    :param graph: The networkx graph.
    :param address: The address to search for.
    :return: The node ID if found, otherwise None.
    """
    for u, v, data in graph.edges(data=True):
        if address.lower() in data.get('name', '').lower():
            return u
    return None