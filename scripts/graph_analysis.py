import sys
import networkx as nx
import networkx.algorithms.community as nxalgo
def community_detection(timeframe):
    DG = nx.read_gexf(f"./data/{timeframe}/{str(timeframe)}_complete_graph.gexf")
    G = nx.Graph(DG)
    c = nxalgo.greedy_modularity_communities(G)
    print(c)

def cycle_detection(timeframe):
    G = nx.read_gexf(f"./data/{timeframe}/{str(timeframe)}_complete_graph.gexf")
    # print(sorted(nx.find_cycle(G, orientation='ignore')))
    print(list(nx.simple_cycles(G, length_bound=2)))

if __name__ == "__main__":
    timeframe = sys.argv[1]
    # community_detection(timeframe)
    cycle_detection(timeframe)