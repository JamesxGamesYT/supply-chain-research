import sys
import os
import json
import pandas as pd
from collections import defaultdict
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def generate_real_data_plot(snapshots):
    """
    Creates plot of charcteristics about real network at certain times
    """
    previous_timeframe_connections = {}
    previous_companies = set()
    lost_connections_counts = []
    gained_connections_counts = []
    lost_companies_counts = []
    gained_companies_counts = []
    reestablished_connections_counts = []
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
    # connections_gained = {}
    # connections_reestablished = defaultdict(dict)
    # connections_reestablished = {}
    for i, timeframe in enumerate(snapshots):
        print(f"\r {i}/{len(snapshots)} snapshots, timeframe: {timeframe}")
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{timeframe}_complete_graph.gexf")
        # if i > 0:
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
    with open("real_data_metrics.json", "w") as f:
        data_dict = {
            "efficencies": efficiencies,
            "clustering_coefficients": clustering_coefficients,
            "average_degrees" : average_degrees,
            "lost_connections_counts" : lost_connections_counts,
            "gained_connections_counts" : gained_connections_counts,
            "lost_companies_counts" : lost_companies_counts,
            "gained_companies_counts" : gained_companies_counts,
        }
        json.dump(data_dict, f)
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
    plt.savefig("real_data_w_legend.png")
    plt.clf()

    plt.plot(snapshots, efficiencies, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("real_efficiencies.png")
    plt.clf()

    plt.plot(snapshots, clustering_coefficients, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("real_clustering_coefficients.png")
    plt.clf()

    plt.plot(snapshots, average_degrees, label="efficency")
    plt.axvline(x=17714)
    plt.axvline(x=18079)
    plt.axvline(x=18809)
    plt.savefig("real_average_degrees.png")
    plt.clf()

    # plt.plot(snapshots, avg_shortest_paths, label="avg_shortest_paths")
    # plt.axvline(x=17714)
    # plt.axvline(x=18079)
    # plt.axvline(x=18809)
    # plt.savefig("real_avg_shorest_paths.png")
    # plt.clf()

def generate_network_shifts(snapshots):
    for i in range(len(snapshots)-1):
        # Just swap base and final and move to next base and final as timeframe advances
        if i == 0:
            base_G = nx.read_gexf(root_dir+f"/data/{snapshots[i]}/{snapshots[i]}_complete_graph.gexf")
            final_G = nx.read_gexf(root_dir+f"/data/{snapshots[i+1]}/{snapshots[i+1]}_complete_graph.gexf")
        else:   
            del base_G
            base_G = final_G
            final_G = nx.read_gexf(root_dir+f"/data/{snapshots[i+1]}/{snapshots[i+1]}_complete_graph.gexf")
        degrees = list(d for n, d in base_G.degree() if d < 100)
        plt.hist(degrees, bins=100)
        plt.savefig(f"{snapshots[i]}_degree_plot.png")

def generate_connections_change(snapshots):
    """
    Generates a json file contaning changes in connections between companies 
    """
    previous_timeframe_connections = {}
    final_timeframe_connections = {}
    companies = set()
    # A dictionary with keys being companies and values of dictionaries of lost companies and their timestamp
    connections_lost = defaultdict(dict)
    connections_gained = defaultdict(dict)
    # connections_reestablished = defaultdict(dict)
    for i, timeframe in enumerate(snapshots):
        print(f"\r {i}/{len(snapshots)} snapshots, timeframe: {timeframe}")
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{timeframe}_complete_graph.gexf")
        companies = companies.union(companies, set(G.nodes))
        for company in G.nodes:
            neighbors = set(G.neighbors(company))
            if company not in previous_timeframe_connections:
                # Consider the edges gained by new companies
                if i == 0:
                    previous_timeframe_connections[company] = neighbors
                    continue
                else:
                    gained = neighbors
                    lost = {}
            else:
                # Compare changes in neighbors (suppliers/customers) over a crisis' time
                previous_neighbors = previous_timeframe_connections[company]
                gained = neighbors.difference(previous_neighbors)
                lost = previous_neighbors.difference(neighbors)
                
            # previous_neighbors = previous_timeframe_connections[company]
            # gained = neighbors.difference(previous_neighbors)
            # if company == "001720-E":
            #     print(timeframe, gained, neighbors)
            # lost = previous_neighbors.difference(neighbors)
            # connections_lost and connections_gained will have all companies that even show up just once
            for lost_company in lost:
                connections_lost[company][lost_company] = timeframe
            # connections_lost[company].update(lost)
            for gained_company in gained:
                connections_gained[company][gained_company] = timeframe
                # if gained_company in connections_lost[company]:
                    # connections_reestablished[company][lost_company] = timeframe
            # This will only stop updating whenever the company leaves the timeframe
            final_timeframe_connections[company] =  neighbors
            previous_timeframe_connections[company] = neighbors

    # Create connection change data
    companies_connections_change = {}
    # Covers all companies that showed up even once
    for company in companies:
        # companies_connections_change[company] = {"lost":{}, "gained":{}, 'incoming_lost':{}, 'incoming_gained':{}, "reestablished":{}}    
        companies_connections_change[company] = {"lost":{}, "gained":{}, 'incoming_lost':{}, 'incoming_gained':{}}    
    for company in companies:
        # Creates connections_change file by combining raw timestamps and company changes
        common_links = set(connections_lost[company].keys()).intersection(set(connections_gained[company].keys()))
        # reestablished_links = set()
        lost_links = set(connections_lost[company]).difference(common_links)
        gained_links = set(connections_gained[company]).difference(common_links)
        for company_link in common_links:
            # It's still reestablished even if it's not there in the end
            # if company_link in final_timeframe_connections[company]:
            # if connections_gained[company][company_link] > connections_lost[company][company_link]:
                # It must've been lost first and then regained
                # reestablished_links.add(company_link)
            # else:
                # It was just lost, even if it disappeared, reappeared, and then disappeared again
            lost_links.add(company_link)
            gained_links.add(company_link)
        for link in lost_links:
            companies_connections_change[company]["lost"][link] = connections_lost[company][link]
            companies_connections_change[link]["incoming_lost"][company] = connections_lost[company][link]
        for link in gained_links:
            companies_connections_change[company]["gained"][link] = connections_gained[company][link]
            companies_connections_change[link]["incoming_gained"][company] = connections_gained[company][link]
        # for link in reestablished_links:
        #     companies_connections_change[company]["reestablished"][link] = connections_gained[company][link]
    # Write to file
    with open(f"./data/2008_companies_connections_change.json", "w") as f:
        json.dump(companies_connections_change, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        date = pd.to_datetime(int(sys.argv[1]), origin='1960-01-01', unit='D')
        print(f"Date: {date}")
    # snapshots = [17714, 17820, 18020, 18079, 18120, 18220, 18320, 18420, 18520, 18620, 18720, 18809, 18820, 18920, 19020, 19120, 19220, 19320, 19420, 19520]
    # snapshots = [17714, 17820, 18020, 18079, 18120, 18220, 18320, 18420, 18520, 18620, 18720, 18809]
    # Quaterly system
    snapshots = [17714, 17806, 17898, 17988, 18079, 18171, 18263, 18353, 18444, 18536, 18628, 18718, 18809]
    # generate_connections_change(snapshots)
    generate_real_data_plot(snapshots)
    # generate_network_shifts(snapshots)