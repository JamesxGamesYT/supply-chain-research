import sys
import os
import json
import scipy.stats
import statsmodels.api as smf
import numpy as np
import random
import time
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 100)

root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def create_parameter_counts(starting_timeframe, ending_timeframe, baseline, undirected_base_G):
    proportion_gained = {}
    proportion_incoming_gained = {}
    proportion_lost = {}
    proportion_incoming_lost = {}

    with open("./data/2008_companies_connections_change.json", "r") as f:
        connections_change = json.load(f)
    for company in undirected_base_G.nodes:
        if company not in connections_change:
            continue
        gained = 0
        for time in connections_change[company]["gained"].values():
            if int(starting_timeframe) < time <= int(ending_timeframe):
                gained += 1
        # proportion_gained[company] = len(connections_change[company]["gained"])
        # proportion_gained[company] = gained
        proportion_gained[company] = gained/baseline[company]
        # proportion_gained[company] = len(connections_change[company]["gained"])/baseline[company]
        lost = 0
        for time in connections_change[company]["lost"].values():
            if int(starting_timeframe) < time <= int(ending_timeframe):
                lost += 1
        # proportion_lost[company] = len(connections_change[company]["lost"])
        # proportion_lost[company] = lost
        proportion_lost[company] = lost/baseline[company]
        # proportion_lost[company] = len(connections_change[company]["lost"])/baseline[company]
        incoming_lost = 0
        for time in connections_change[company]["incoming_lost"].values():
            if int(starting_timeframe) < time <= int(ending_timeframe):
                # print("added!")
                incoming_lost += 1
        # proportion_lost[company] = len(connections_change[company]["lost"])
        # proportion_incoming_lost[company] = incoming_lost
        proportion_incoming_lost[company] = incoming_lost/baseline[company]
        # proportion_lost[company] = len(connections_change[company]["lost"])/baseline[company]
        incoming_gained = 0
        for time in connections_change[company]["incoming_gained"].values():
            if int(starting_timeframe) < time <= int(ending_timeframe):
                incoming_gained += 1
        # proportion_lost[company] = len(connections_change[company]["lost"])
        # proportion_incoming_gained[company] = incoming_gained
        proportion_incoming_gained[company] = incoming_gained/baseline[company]
        # proportion_lost[company] = len(connections_change[company]["lost"])/baseline[company]
    # print(proportion_incoming_lost)

    return proportion_incoming_lost, proportion_lost, proportion_incoming_gained, proportion_gained

def company_network_analysis(timeframes):
    baseline = {}
    connection_lengths = {}
    company_country = {}
    company_size = {}
    with open("./data/2008_companies_connections_change.json", "r") as f:
        connections_change = json.load(f)
    for i in range(len(timeframes)-1):
        # Just swap base and final and move to next base and final as timeframe advances
        if i == 0:
            undirected_base_G = nx.read_gexf(root_dir+f"/data/{timeframes[i]}/{timeframes[i]}_complete_graph.gexf")
            undirected_final_G = nx.read_gexf(root_dir+f"/data/{timeframes[i+1]}/{timeframes[i+1]}_complete_graph.gexf")
        else:   
            del undirected_base_G
            undirected_base_G = undirected_final_G
            undirected_final_G = nx.read_gexf(root_dir+f"/data/{timeframes[i+1]}/{timeframes[i+1]}_complete_graph.gexf")
        # Companies that are the same between the two frames
        companies = set(undirected_base_G.nodes).intersection(set(undirected_final_G.nodes))
        print("Graphs loaded, companies:", len(companies))
        print(len(set(undirected_base_G.nodes).difference(companies)), "Nodes removed out of ", len(undirected_base_G.nodes))
        print(len(set(undirected_final_G.nodes).difference(companies)), "Nodes added out of", len(undirected_final_G.nodes))
        # Calculate company size at base using both incoming and outgoing edges
        actual_undirected_base_G = undirected_base_G.to_undirected()
        for company in undirected_base_G.nodes:
            baseline[company] = len(list(actual_undirected_base_G.neighbors(company)))
            company_size[company] = baseline[company] 
            company_country[company] = actual_undirected_base_G.nodes[company]["country"]
        i = 0
        print("Company sizes created")
        # for edge in undirected_base_G.edges:
        #     # print(undirected_base_G.edges[edge]["history"])
        #     # print(type(undirected_base_G.edges[edge]["history"]))
        #     connection_lengths[(edge)] = int(undirected_base_G.edges[edge]["history"][36:41]) - int(undirected_base_G.edges[edge]["history"][29:34])
        # # for i_company in companies:
        # #     for j_company in companies:
        # #             if i_company == j_company:
        # #                 continue
        # #             if j_company in connections_change[i_company]["reestablished"] :
        # #                 connection_lengths[((i_company, j_company))] = int(connections_change[i_company]["lost"][j_company]) - int(undirected_base_G.edges[edge]["history"][29:34])
        # #             elif j_company in connections_change[i_company]["lost"]:
        # #                 connection_lengths[((i_company, j_company))] = int(undirected_base_G.edges[edge]["history"][36:41]) - int(undirected_base_G.edges[edge]["history"][29:34])
        # #                 print(undirected_base_G.edges[edge]["history"], connection_lengths[((i_company, j_company))], i_company, j_company)
        # # frozenset({'00B76Z-E', '060DD3-E'})
        # #         else:
        # #             proportion_gained[company] = len(G.neighbors)
        print("Connections length created")
        proportion_incoming_lost, proportion_lost, proportion_incoming_gained, proportion_gained = create_parameter_counts(timeframes[i], timeframes[i+1], baseline, undirected_base_G)
        lost_edge_matrix = {"lost":[], "incoming_first":[], "outgoing_first":[], "incoming_second":[], "outgoing_second":[], "incoming_company_size":[], "outgoing_company_size":[], "same_country":[], "intercept":[]}
        gained_edge_matrix = {"gained":[], "incoming_first":[], "outgoing_second":[], "outgoing_first":[], "incoming_second":[], "outgoing_second":[], "incoming_company_size":[], "outgoing_company_size":[], "same_country":[], "intercept":[]}
        # reestablished_edge_matrix = {"reestablished":[], "incoming_first":[], "outgoing_second":[], "outgoing_first":[], "incoming_second":[], "outgoing_second":[], "incoming_company_size":[], "outgoing_company_size":[], "connection_length":[]}
        # reestablished_edge_matrix = {"reestablished":[], "incoming_first":[], "outgoing_second":[], "outgoing_first":[], "incoming_second":[], "outgoing_second":[], "incoming_company_size":[], "outgoing_company_size":[], "same_country":[]}
        print("Parmaeters created")
        gained_true = 0
        gained_false = 0
        gained_total_num = 0
        total_possible = 0
        for i_company in companies:
            # if i_company not in undirected_final_G.nodes:
                # continue
            for j_company in companies:
                # if j_company not in undirected_final_G.nodes:
                    # continue
                if i_company == j_company:
                    continue
                # if j_company in connections_change[i_company]["reestablished"] or j_company in connections_change[i_company]["lost"]:
                    # print("YOO!")
                    # print(connections_change[i_company]["reestablished"], connections_change[i_company]["lost"], j_company)
                if j_company in undirected_base_G.neighbors(i_company):
                    # if company_country[i_company] == company_country[j_company]:
                    if j_company in undirected_final_G.neighbors(i_company):
                        lost_edge_matrix["lost"].append(False)
                    else:
                        lost_edge_matrix["lost"].append(True)
                    lost_edge_matrix["incoming_first"].append(proportion_incoming_lost[i_company])
                    lost_edge_matrix["outgoing_second"].append(proportion_lost[j_company])
                    lost_edge_matrix["outgoing_first"].append(proportion_lost[i_company])
                    lost_edge_matrix["incoming_second"].append(proportion_incoming_lost[j_company])
                    lost_edge_matrix["incoming_company_size"].append(company_size[i_company])
                    lost_edge_matrix["outgoing_company_size"].append(company_size[j_company])
                    lost_edge_matrix["same_country"].append(int(company_country[i_company] == company_country[j_company]))
                    lost_edge_matrix["intercept"].append(1)
                    # if len(lost_edge_matrix["lost"]) < 101:
                        # print("SAME COMPANY!", i_company, j_company, len(lost_edge_matrix["lost"]), int(company_country[i_company] == company_country[j_company]))
                # Gained nodes
                elif j_company in undirected_final_G.neighbors(i_company):
                    gained_edge_matrix["gained"].append(True)
                    gained_edge_matrix["incoming_first"].append(proportion_incoming_gained[i_company])
                    gained_edge_matrix["outgoing_second"].append(proportion_gained[j_company])
                    gained_edge_matrix["outgoing_first"].append(proportion_gained[i_company])
                    gained_edge_matrix["incoming_second"].append(proportion_incoming_gained[j_company])
                    gained_edge_matrix["incoming_company_size"].append(company_size[i_company])
                    gained_edge_matrix["outgoing_company_size"].append(company_size[j_company])
                    gained_edge_matrix["same_country"].append(int(company_country[i_company] == company_country[j_company]))
                    gained_edge_matrix["intercept"].append(1)
                    gained_true += 2
                    gained_total_num += 2
                        # if undirected_final_G.nodes
                        # gained_edge_matrix["same_country"]
                # Edge that just wasn't gained
                else:
                    if gained_true > gained_false:
                        gained_edge_matrix["gained"].append(False)
                        gained_edge_matrix["incoming_first"].append(proportion_incoming_gained[i_company])
                        gained_edge_matrix["outgoing_second"].append(proportion_gained[j_company])
                        gained_edge_matrix["outgoing_first"].append(proportion_gained[i_company])
                        gained_edge_matrix["incoming_second"].append(proportion_incoming_gained[j_company])
                        gained_edge_matrix["incoming_company_size"].append(company_size[i_company])
                        gained_edge_matrix["outgoing_company_size"].append(company_size[j_company])
                        gained_edge_matrix["same_country"].append(int(company_country[i_company] == company_country[j_company]))
                        gained_edge_matrix["intercept"].append(1)
                        gained_false += 1
                    gained_total_num += 1
                total_possible += 1
                # Either use an else if to analyze reestablished links
                # if j_company in connections_change[i_company]["reestablished"] or j_company in connections_change[i_company]["lost"]:
                #     if j_company in connections_change[i_company]["reestablished"]:
                #         if int(timeframes[i]) < connections_change[i_company]["reestablished"][j_company] <= int(timeframes[i+1]):
                #             pass
                #         else:
                #             continue
                #     if j_company in connections_change[i_company]["lost"]:
                #         # Lost connections from before this timeframe can still be repaired
                #         if int(connections_change[i_company]["lost"][j_company]) <= int(timeframes[i+1]):
                #             pass
                #         else:
                #             continue
                #     if j_company in undirected_final_G.neighbors(i_company):
                #         reestablished_edge_matrix["reestablished"].append(True)
                #         reestablished_edge_matrix["incoming_first"].append(proportion_incoming_gained[i_company])
                #         reestablished_edge_matrix["outgoing_second"].append(proportion_gained[j_company])
                #         reestablished_edge_matrix["outgoing_first"].append(proportion_gained[i_company])
                #         reestablished_edge_matrix["incoming_second"].append(proportion_incoming_gained[j_company])
                #         # reestablished_edge_matrix["connection_length"].append(connection_lengths[((i_company, j_company))])
                #         reestablished_edge_matrix["incoming_company_size"].append(company_size[i_company])
                #         reestablished_edge_matrix["outgoing_company_size"].append(company_size[j_company])
                #         # Or add it as a possible factor
                #         # if j_company in connections_change[i_company]["reestablished"]:
                #         #     gained_edge_matrix["reestablished"] = 1
                #         # else:
                #         #     gained_edge_matrix["reestablished"] = 0
                #         # print(proportion_gained[i_company], proportion_gained[j_company], i_company, j_company)
                #     else:
                #         reestablished_edge_matrix["reestablished"].append(False)
                #         reestablished_edge_matrix["incoming_first"].append(proportion_incoming_gained[i_company])
                #         reestablished_edge_matrix["outgoing_second"].append(proportion_gained[j_company])
                #         reestablished_edge_matrix["outgoing_first"].append(proportion_gained[i_company])
                #         reestablished_edge_matrix["incoming_second"].append(proportion_incoming_gained[j_company])
                #         # reestablished_edge_matrix["connection_length"].append(connection_lengths[((i_company, j_company))])
                #         reestablished_edge_matrix["incoming_company_size"].append(company_size[i_company])
                #         reestablished_edge_matrix["outgoing_company_size"].append(company_size[j_company])
                        # if j_company in connections_change[i_company]["reestablished"]:
                        #     reestablished_edge_matrix["reestablished"] = 1
                        # else:
                        #     reestablished_edge_matrix["reestablished"] = 0
        print("Edge matrices created!")
        print("dfs created!")
        lost_df = pd.DataFrame.from_dict(lost_edge_matrix)
        print(lost_df.head(20).to_string())
        lost_true = lost_df[lost_df["lost"] == True]
        lost_false = lost_df[lost_df["lost"] == False]
        print(f"# of Lost connections (true) {len(lost_true)}, # of not lost connections (false) {len(lost_false)}")
        # lost_false = lost_false.loc[np.random.choice(lost_false.index, size=len(lost_true))]
        # lost_total = pd.concat([lost_false, lost_true])

        # reestablished_df = pd.DataFrame.from_dict(reestablished_edge_matrix)
        # print(reestablished_df)
        # reestablished_true = reestablished_df[reestablished_df["reestablished"] == True]
        # reestablished_false = reestablished_df[reestablished_df["reestablished"] == False]
        # reestablished_false = reestablished_false.loc[np.random.choice(reestablished_false.index, size=len(reestablished_true))]
        # reestablished_total = pd.concat([reestablished_false, reestablished_true])
        # print(f"# of reestablished connections (true) {len(reestablished_true)}, # of not reestablished connections (false) {len(reestablished_false)}")

        gained_df = pd.DataFrame.from_dict(gained_edge_matrix)
        print(gained_df.head(20).to_string())
        gained_true = gained_df[gained_df["gained"] == True]
        gained_false = gained_df[gained_df["gained"] == False]
        # gained_false = gained_false.loc[np.random.choice(gained_false.index, size=len(gained_true))]
        # gained_total = pd.concat([gained_false, gained_true])
        print(f"# of gained connections (true) {len(gained_true)}, # of not gained connections (false) {len(gained_false)}")
        lost_probit = smf.Probit(lost_df["lost"], lost_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country", "intercept"]])
        # lost_probit = smf.Probit(lost_total["lost"], lost_total[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]])
        # reestablished_probit = smf.Probit(reestablished_total["reestablished"], reestablished_total[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "connection_length", "incoming_company_size", "outgoing_company_size"]])
        # reestablished_probit = smf.Probit(reestablished_total["reestablished"], reestablished_total[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size"]])
        gained_probit = smf.Probit(gained_df["gained"], gained_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country", "intercept"]])
        # gained_probit = smf.Probit(gained_total["gained"], gained_total[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]])
        lost_result=lost_probit.fit()
        print(lost_result.summary2())
        # print(lost_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]].shape)
        # print(lost_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]].head(1).shape)
        # print(lost_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]].head(1))
        # predictions = lost_probit.predict(params=lost_df[["incoming_first", "outgoing_second", "outgoing_first", "incoming_second", "incoming_company_size", "outgoing_company_size", "same_country"]].head(1))
        # predictions = lost_probit.predict(lost_probit.params)
        # print(predictions, "predictions")
        # print(predictions.shape)
        # reestablished_result=reestablished_probit.fit()
        # print(reestablished_result.summary2())
        gained_result=gained_probit.fit()
        print(gained_result.summary2())

        # print("Average probability of loss", len(lost_true)/len(lost_df), len(lost_true),len(lost_df))
        # print("Average probability of reestablishment", len(reestablished_true)/len(reestablished_df), len(reestablished_true),len(reestablished_df))
        # print("Average probability of gained", len(gained_true)/gained_total_num, len(gained_true),gained_total_num)
        # print("Average probability gained overall total", len(gained_true)/total_possible, len(gained_true), total_possible)
        print("Average proportion of lost incoming_first", lost_df["incoming_first"].sum()/len(lost_df))
        print("Average proportion of lost outgoing_first", lost_df["outgoing_first"].sum()/len(lost_df))
        print("Average proportion of lost incoming_second", lost_df["incoming_second"].sum()/len(lost_df))
        print("Average proportion of lost outgoing_second", lost_df["outgoing_second"].sum()/len(lost_df))
        # print("Average proportion of reestablished incoming_first", reestablished_df["incoming_first"].sum()/len(reestablished_df))
        # print("Average proportion of reestablished outgoing_first", reestablished_df["outgoing_first"].sum()/len(reestablished_df))
        # print("Average proportion of reestablished incoming_second", reestablished_df["incoming_second"].sum()/len(reestablished_df))
        # print("Average proportion of reestablished outgoing_second", reestablished_df["outgoing_second"].sum()/len(lost_df))
        print("Average proportion of gained incoming_first", gained_df["incoming_first"].sum()/len(gained_df))
        print("Average proportion of gained outgoing_first", gained_df["outgoing_first"].sum()/len(gained_df))
        print("Average proportion of gained incoming_second", gained_df["incoming_second"].sum()/len(gained_df))
        print("Average proportion of gained outgoing_second", gained_df["outgoing_second"].sum()/len(gained_df))


def probability_compute_fun(x,G,type_str):
    if type_str=='lost':
        threshold = scipy.stats.norm.cdf(
            1.0363*(G.nodes[x[0]]['incoming_lost'])+
            1.9283*(G.nodes[x[1]]['lost'])+
            1.0363*(G.nodes[x[0]]['lost'])+
            1.0363*(G.nodes[x[1]]['incoming_lost'])+
            -0.0027*(G.nodes[x[0]]['company_size']) +
            -0.0025*(G.nodes[x[1]]['company_size']))
        if random.random() < threshold:
            return 1
        else:
            return 0
    if type_str=='reestablish':
        if random.random() < 0.02415747092156278:
            return 1
        else:
            return 0
    if type_str=='gain':
        threshold = scipy.stats.norm.cdf(
            0.4843*(G.nodes[x[0]]['incoming_gained'])+
            0.3618*(G.nodes[x[1]]['gained'])+
            0.3650*(G.nodes[x[0]]['gained'])+
            0.4797*(G.nodes[x[1]]['incoming_gained'])+
            0.0094*(G.nodes[x[0]]['company_size']) +
            0.0093*(G.nodes[x[1]]['company_size']))
        if random.random() < threshold:
            return 1
        else:
            return 0
        return 1

def simulation(timeframes):
    G = nx.read_gexf(root_dir+f"/data/{timeframes[0]}/{timeframes[0]}_complete_graph.gexf")
    undirected_base_G = G.to_undirected()
    print("Graph read", len(G.nodes))
    # Count sizes of companies based on initial number of neighbors
    baseline_size = {}
    for company in undirected_base_G.nodes:
        baseline_size[company] = len(list(undirected_base_G.neighbors(company)))
    # Generate counts
    proportion_incoming_lost, proportion_lost, proportion_incoming_gained, proportion_gained = create_parameter_counts(timeframes[0], timeframes[1], baseline, undirected_base_G)
    print("Parameters created")
    for node in G:
        G.nodes[node]["incoming_lost"] = proportion_incoming_lost[node]
        G.nodes[node]["lost"] = proportion_lost[node]
        G.nodes[node]["incoming_gained"] = proportion_incoming_gained[node]
        G.nodes[node]["gained"] = proportion_gained[node]
        G.nodes[node]["company_size"] = baseline_size[node]
    print("Node parameters assigned")

    timesteps=10
    NODE_LOSE_PROB = 1229/9541
    NODE_GAIN_PROB = 714/9026
    NODE_GAIN_PROBABILITY = 0.00009412135012690604
    removed_edge_set = set()
    edge_counts = [len(G.edges())]
    node_counts = [len(G.nodes())]
    removed_edges = [0]
    reestablished_edges = [0]
    added_edges = [0]
    efficiencies = [nx.local_efficiency(G.to_undirected())]
    for i in range(1, timesteps+1):
        node_counts.append(len(G.nodes()))
        # Create erdos renyi graph from existing graph to analyze limited number of potential edges
        G_potential=nx.erdos_renyi_graph(G.number_of_nodes(), NODE_GAIN_PROBABILITY, directed=True)
        # G_potential=nx.fast_gnp_random_graph(G.number_of_nodes(), NODE_GAIN_PROBABILITY, directed=True)
        print("Potential graph created")
        name_mapping = {}
        for j, node in enumerate(G.nodes):
            G_potential.nodes[j]["incoming_lost"] = proportion_incoming_lost[node]
            G_potential.nodes[j]["lost"] = proportion_lost[node]
            G_potential.nodes[j]["incoming_gained"] = proportion_incoming_gained[node]
            G_potential.nodes[j]["gained"] = proportion_gained[node]
            G_potential.nodes[j]["company_size"] = baseline_size[node]
            name_mapping[j] = node
        nx.relabel_nodes(G_potential, name_mapping, copy=False)
        print("Potential graph relabeled")
        print(f"Timestep: {i}")
        start_time=time.time()
        existing_edge_set=set(G.edges())
        remove_probability=list(map(lambda x: probability_compute_fun(x,G,'lost'), existing_edge_set))
        # print("probabilities calculated")
        check_remove= np.array(remove_probability)==1
        remove_edge_set = np.array(list(existing_edge_set))[check_remove]
        print('lost process', len(existing_edge_set),len(remove_edge_set))

        reestablish_probability = list(map(lambda x: probability_compute_fun(x,G,'reestablish'), removed_edge_set))
        check_reestablish = np.array(reestablish_probability)==1
        reestablish_edge_set = np.array(list(removed_edge_set))[check_reestablish]
        print('reestablish process', len(removed_edge_set), len(reestablish_edge_set))

        G.remove_edges_from(remove_edge_set)
        G.add_edges_from(reestablish_edge_set)
        remove_node_set = []
        for node in G:
            if len(list(G.neighbors(node))) == 0:
                remove_node_set.append(node)
        G.remove_nodes_from(remove_node_set)

        print(len(G_potential.edges()), len(existing_edge_set), len(removed_edge_set))
        potential_edge_set=set(G_potential.edges()).difference(existing_edge_set).difference(removed_edge_set)
        add_probability=list(map(lambda x: probability_compute_fun(x,G_potential,'gain'), potential_edge_set))
        # print("probabilities calculated")
        check_add= np.array(add_probability)==1
        # print("check mfw")
        add_edge_set= np.array(list(potential_edge_set))[check_add]
        print('gain process', len(potential_edge_set), len(add_edge_set))

        removed_edge_set.update(set([(edge[0], edge[1]) for edge in remove_edge_set]))
        removed_edge_set = removed_edge_set.difference(set(set([(edge[0], edge[1]) for edge in reestablish_edge_set])))
        outdated_removed_edges = []
        for removed_edge in removed_edge_set:
            if removed_edge[0] not in G.nodes or removed_edge[1] not in G.nodes:
                outdated_removed_edges.append(removed_edge)
        for edge in outdated_removed_edges:
            removed_edge_set.remove(edge)
        # G_add_edge_set = {(name_mapping[node0], name_mapping[node1]) for (node0, node1) in add_edge_set}
        # G.add_edges_from(G_add_edge_set)
        G.add_edges_from(add_edge_set)
        edge_counts.append(len(G.edges()))
        removed_edges.append(len(remove_edge_set))
        reestablished_edges.append(len(reestablish_edge_set))
        added_edges.append(len(add_edge_set))
        efficiencies.append(nx.local_efficiency(G.to_undirected()))
        end_time=time.time()
        print(len(G.edges()), len(remove_edge_set), len(reestablish_edge_set), len(add_edge_set))
        print('used seconds', end_time-start_time, "\n")
    plt.plot([i for i in range(timesteps+1)], node_counts, label="node count")
    plt.plot([i for i in range(timesteps+1)], edge_counts, label="edge count")
    plt.plot([i for i in range(timesteps+1)], removed_edges, label="removed edges")
    plt.plot([i for i in range(timesteps+1)], reestablished_edges, label="reestablished edges")
    plt.plot([i for i in range(timesteps+1)], added_edges, label="added edges")
    plt.legend()
    plt.savefig("simulated_model_overview_w_legend.png")
    print(efficiencies)
    return G
# G=nx.erdos_renyi_graph(1000,0.05)
# print(G.number_of_edges())
# for i in G.nodes():
#     G.nodes[i]['lost']=random.random()
#     G.nodes[i]['gain']=random.random() 
# print(G.nodes[0])

# ####start_simulation
# new_G=simulation(G)

                
if __name__ == "__main__":
    timeframe = sys.argv[1]
    if timeframe == "2008":
        # timeframes = ["17540", "17620", "17720", "17820", "18020", "18120", "18220", "18320", "18420", "18520", "18620", "18720", "18820", "18920", "19020", "19120", "19220", "19320", "19420", "19520"]
        # timeframes = ["17540", "18220", "18820",  "19420", ]
        # Jul 1st 2008, Jul 1st 2009, Jul 1st 2011
        timeframes = ["17714", "18079", "18809"]
        # timeframes = ["17540", "18920", "19520"]
        # timeframes = ["17540", "19520"]
        # timeframes = ["21870"]
    if timeframe == "covid":
        timeframes = ["21870", "21930", "21960", "22000", "22100", "22200", "22300", "22370"]
    company_network_analysis(timeframes)
    # simulation(timeframes)