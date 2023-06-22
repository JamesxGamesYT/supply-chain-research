import pandas as pd
import networkx as nx
import random
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import sys

root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def remove_nodes(G, timeframe):
    nodes_to_remove = nx.isolates(G)
    # print(list(nodes_to_remove))
    for node in list(nodes_to_remove):
        G.remove_node(node)
    return G


def add_nodes(G, timeframe, distribution):
    pass


def remove_edges(G, timeframe):
    edges_to_remove = []
    for edge in G.edges:
        if random.random() < 0.03:
            edges_to_remove.append(edge)
    for edge in edges_to_remove:
        G.remove_edge(edge[0], edge[1])
    return G

def add_edges(G, timeframe):
    edges_to_add = []
    G_potential = nx.erdos_renyi_graph(len(G.nodes), 0.02)
    name_mapping = {}
    for j, node in enumerate(G.nodes):
        name_mapping[j] = node
    nx.relabel_nodes(G_potential, name_mapping, copy=False)
    # for node in G.nodes:
    #     for other_node in G.nodes:
    #         if random.random() < 0.000001:
    #             edges_to_add.append((node, other_node))
    # for edge in edges_to_add:
    for edge in G_potential.edges():
        G.add_edge(edge)
    return G

def simulate(timeframes):
    G = nx.read_gexf(root_dir+f"/data/{timeframes[0]}/{timeframes[0]}_complete_graph.gexf")
    degrees = pd.Series(sorted([d for n, d in G.degree()], reverse=True)).value_counts(normalize=True, ascending=True)
    print(degrees)
    print(degrees.cumsum())
    previous_timeframe_connections = {}
    previous_companies = set()
    lost_connections_counts = []
    gained_connections_counts = []
    lost_companies_counts = []
    gained_companies_counts = []
    total_connections_counts = []
    total_nodes_counts = []
    connections_lost = defaultdict(dict)
    # connections_lost = {}
    connections_gained = defaultdict(dict)
    efficiencies = []
    # connected_components_distribution = []
    avg_shortest_paths = []
    clustering_coefficients = []
    average_degrees = []
    for i in range(5):
        G = remove_edges(G, None)
        G = remove_nodes(G, None)
        # G = add_nodes(G, None, degrees.cumsum())
        undirected_G = G.to_undirected()
        efficiencies.append(nx.local_efficiency(undirected_G))
        # Doesn't work, graph not completely connected (but like 99% connected)
        # avg_shortest_paths.append(nx.average_shortest_path_length(undirected_G))
        # connected_components_distribution.append([len(c) for c in sorted(nx.connected_components(undirected_G), key=len, reverse=True)])
        clustering_coefficients.append(sum(nx.clustering(undirected_G).values())/len(G.nodes))
        degrees = undirected_G.degree()
        sum_of_edges = sum(dict(degrees).values())
        average_degrees.append(sum_of_edges/len(G.nodes))
        gained_connections_count = 0
        lost_connections_count = 0
        reestablished_connections_count = 0
        total_nodes_counts.append(len(G.nodes))
        total_connections_counts.append(len(G.edges))
        for company in G.nodes:
            neighbors = set(G.neighbors(company))
            if company not in previous_timeframe_connections:
                if i == 0:
                    previous_timeframe_connections[company] = neighbors
                    previous_companies.add(company)
                    continue
                else:
                    gained = neighbors
                    lost = {}
            else:
                # Compare changes in neighbors (suppliers/customers) over a crisis' time
                previous_neighbors = previous_timeframe_connections[company]
                gained = neighbors.difference(previous_neighbors)
                lost = previous_neighbors.difference(neighbors)


            # connections_lost and connections_gained will have all companies that even show up just once
            for lost_company in lost:
                lost_connections_count += 1
                connections_lost[company][lost_company] = timeframe
            # connections_lost[company].update(lost)
            for gained_company in gained:
                connections_gained[company][gained_company] = timeframe
                gained_connections_count += 1
                # if gained_company in connections_lost[company]:
                    # reestablished_connections_count += 1
                    # connections_reestablished[company][lost_company] = timeframe
            previous_timeframe_connections[company] = neighbors
        # Compute difference between previously gained connections
        gained_connections_counts.append(gained_connections_count)
        lost_connections_counts.append(lost_connections_count)
        # reestablished_connections_counts.append(reestablished_connections_count)
        gained_companies_counts.append(len(set(G.nodes).difference(previous_companies)))
        lost_companies_counts.append(len(previous_companies.difference(set(G.nodes))))
        print(lost_connections_counts[-1], "lost connections count")
        print(gained_connections_counts[-1], "gained connections count")
        print(lost_companies_counts[-1], "lost companies count")
        print(gained_companies_counts[-1], "gained companies count")
    snapshots = [int(time) for time in timeframes]
    plt.plot(snapshots, lost_connections_counts, label="removed edges")
    plt.plot(snapshots, gained_connections_counts, label="added edges")
    plt.plot(snapshots, lost_companies_counts, label="removed companies")
    plt.plot(snapshots, gained_companies_counts, label="added companies")
    # plt.plot(snapshots, reestablished_connections_counts, label="reestablished edges")
    plt.plot(snapshots, total_connections_counts, label="total edges")
    plt.plot(snapshots, total_nodes_counts, label="total_nodes")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.legend()
    plt.savefig("simulated_data_w_legend.png")
    plt.clf()

    plt.plot(snapshots, efficiencies, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("simulated_efficiencies.png")
    plt.clf()

    plt.plot(snapshots, clustering_coefficients, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("simulated_clustering_coefficients.png")
    plt.clf()

    plt.plot(snapshots, average_degrees, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("simulated_average_degrees.png")
    plt.clf()
if __name__ == "__main__":
    timeframe = sys.argv[1]
    if timeframe == "shock":
        # Jul 1st 2008, Oct 1st 2008, Jan 1st 2009, Apr 1st 2009, Jul 1st 2009, 
        timeframes = ["17714", "17806", "17898", "17988", "18079"]
    if timeframe == "recovery":
        # Jul 1st 2009, Oct 1st 2009, Jan 1st 2010, Apr 1st 2010, Jul 1st 2010, Oct 1st 2010, Jan 1st 2011, Ap 1st 2011, Jul 1st 2011
        timeframes = ["18079", "18171", "18263", "18353", "18444", "18536", "18628", "18718", "18809"]
    simulate(timeframes)