import numpy as np
import random
#---------------------------------------------------------------------------------------------------
def make_fc_net(size):
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Size must be positive integer")

    network = np.ones((size, size), dtype=int)
    np.fill_diagonal(network, 0)
    return network
#---------------------------------------------------------------------------------------------------
def make_ring_net(size, k_neighbours): #maybe unnecessary, can just use W-Strogatz with p_rewire == 0
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Size must be positive integer")
    if not isinstance(k_neighbours, int) or k_neighbours <= 0:
        raise ValueError("K Neighbours must be positive integer")
    if k_neighbours >= size - 1:
        raise ValueError("Neighbours must be < (size - 1)")
    if k_neighbours % 2 != 0:
        raise ValueError("Neighbours must be even to avoid asymmetrical connections")
    network = np.zeros((size, size), dtype=int)

    for i in range(size):
        for offset in range(1, ((k_neighbours// 2) + 1)):
            neighbour_right = (i + offset) % size
            network[i][neighbour_right] = 1
            network[neighbour_right][i] = 1

            neighbour_left = (i - offset) % size
            network[i][neighbour_left] = 1
            network[neighbour_left][i] = 1

    return network
#---------------------------------------------------------------------------------------------------
def make_sw_net(size, k_neighbours, p_rewire):
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Size must be positive integer")
    if not isinstance(k_neighbours, int) or k_neighbours <= 0:
        raise ValueError("K Neighbours must be positive integer")
    if k_neighbours >= size:
        raise ValueError("Neighbours must be < size")
    if k_neighbours == (size - 1):
        return make_fc_net(size)
    if k_neighbours % 2 != 0:
        raise ValueError("Neighbours must be even to avoid asymmetrical connections")
    if not (0.0 <= p_rewire <= 1.0):
        raise ValueError("Rewiring probability (p_rewire) must be between 0.0 and 1.0.")
    
    edges = set()
    for i in range(size):
        for offset in range(1, ((k_neighbours// 2) + 1)):
            neighbour_right = (i + offset) % size
            u, v = (i, neighbour_right) if i < neighbour_right else (neighbour_right, i)
            edges.add((u,v))
    
    edges_to_rewire = list(edges)
    for u, v in edges_to_rewire:
        if random.random() < p_rewire:
            edges.remove((u,v))
            new_v = None
            while new_v is None:
                potential_new_v = random.randint(0, size - 1)
                if potential_new_v != u:
                    potential_edge = (u, potential_new_v) if u < potential_new_v else (potential_new_v, u)
                    if potential_edge not in edges:
                        new_v = potential_new_v
            final_edge = (u, new_v) if u < new_v else (new_v, u)
            edges.add(final_edge)

    network = np.zeros((size, size), dtype=int)
    for u,v in edges:
        network[u][v] = 1
        network[v][u] = 1
    return network
#---------------------------------------------------------------------------------------------------