import sys
import networkx as nx
import networkx.algorithms.community as nxalgo
def community_detection(timeframe):
    DG = nx.read_gexf(f"../data/{timeframe}/{str(timeframe)}_complete_graph.gexf")
    G = nx.Graph(DG)
    c = nxalgo.greedy_modularity_communities(G)
    print(c)

if __name__ == "__main__":
    timeframe = sys.argv[1]
    community_detection(timeframe)