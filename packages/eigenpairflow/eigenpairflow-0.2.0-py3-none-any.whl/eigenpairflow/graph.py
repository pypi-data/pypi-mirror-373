import networkx as nx


def create_n_partite_graph(partition_sizes, edge_lengths_dict):
    """
    Creates an n-partite graph based on partition sizes and edge lengths between partitions.

    Args:
        partition_sizes (list): A list of integers representing the number of nodes in each partition.
        edge_lengths_dict (dict): A dictionary where keys are tuples of partition indices (i, j)
                                  and values are the lengths of edges between nodes in partition i and partition j.

    Returns:
        nx.Graph: The constructed n-partite graph.
    """
    G = nx.Graph()
    node_id = 1
    partition_nodes = []

    # Add nodes to each partition
    for i, size in enumerate(partition_sizes):
        nodes_in_partition = list(range(node_id, node_id + size))
        G.add_nodes_from(nodes_in_partition, type=f"p{i}")
        partition_nodes.append(nodes_in_partition)
        node_id += size

    # Add edges between partitions with specified lengths
    for (p1_idx, p2_idx), length in edge_lengths_dict.items():
        if (
            p1_idx < len(partition_sizes)
            and p2_idx < len(partition_sizes)
            and p1_idx != p2_idx
        ):
            for u in partition_nodes[p1_idx]:
                for v in partition_nodes[p2_idx]:
                    G.add_edge(u, v, length=length, weight=1 / length)

    return G
