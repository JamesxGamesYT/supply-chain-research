import networkx as nx
import pandas as pd
import numpy as np
import os
import sys
import json
import itertools
import pathlib
root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
# with open(root_dir+"/data/complete_graph.gexf", "r") as f:
    # print("THIS WORKS")
# from classes import *
countries = {'PK', "nan", 'TW', 'ME', 'AU', 'BH', 'TO', 'BN', 'XK', 'MK', 'FI', 'FM', 'GE', 'SZ', 'KE', 'TJ', 'IT', 
'CH', 'GT', 'DK', 'AD', 'UZ', 'MT', 'MH', 'CN', 'GL', 'TN', 'GN', 'JO', 'VI', 'AI', 'MU', 'BM', 'CF', 'AT', 'BD', 
'CU', 'DZ', 'AS', 'PL', 'MQ', 'ID', 'MA', 'AZ', 'GM', 'MR', 'LB', 'CL', 'LV', 'VN', 'IS', 'KW', 'IQ', 'BW', 'SG', 
'HR', 'BA', 'MV', 'BZ', 'UA', 'HT', 'CR', 'PR', 'BF', 'HN', 'AG', 'GY', 'NG', 'IL', 'GR', 'PS', 'AF', 'CZ', 'NP', 
'LI', 'ER', 'GQ', 'BI', 'KR', '0', 'US', 'AM', 'EC', 'NC', 'AN', 'SA', 'PA', 'CV', 'IE', 'CI', 'BE', 'YE', 'LC', 
'ES', 'LR', 'BT', 'NZ', 'MZ', 'SM', 'MM', 'SL', 'KI', 'RU', 'TH', 'VE', 'TT', 'DE', 'TM', 'CM', 'SE', 'JM', 'AW', 
'BY', 'MW', 'MC', 'LU', 'BR', 'GA', 'EE', 'TV', 'RW', 'KG', 'BG', 'IR', 'KN', 'BS', 'PW', 'MG', 'DJ', 'UG', 'SC', 
'PF', 'MX', 'SR', 'EG', 'GU', 'RS', 'WS', 'AR', 'AL', 'SS', 'SB', 'CA', 'NO', 'VA', 'IN', 'AX', 'KM', 'LY', 'MY', 
'TZ', 'SO', 'ZW', 'BB', 'FR', 'ZA', 'KH', 'HK', 'TR', 'SY', 'CD', 'PT', 'SK', 'NE', 'NI', 'SN', 'CG', 'SV', 'PG', 
'TD', 'BO', 'BJ', 'QA', 'GH', 'CO', 'KP', 'LT', 'ST', 'ML', 'JP', 'RE', 'TG', 'MO', 'LA', 'AE', 'ZM', 'KY', 'OM', 
'RO', 'SI', 'VU', 'MD', 'FO', 'KZ', 'TL', 'VC', 'ET', 'CY', 'UY', 'GI', 'MN', 'SD', 'HU', 'VG', 'FJ', 'LK', 'AO', 
'GB', 'DM', 'DO', 'PY', 'PE', 'PH', 'NL'}

types = {"nan", 'CAC', 'SHP', 'OPD', 'PEF', 'ESP', 'PVT', 'PVF', 'TRU', 'SOV', 'PRO', 'COL', 'BRA', 'FAF', 'JVT', 
'SUB', 'HED', 'MUT', 'COR', 'UMB', 'PRT', 'UIT', 'MED', 'MUE', 'BAS', 'PUB', 'ABS', 'MUC', 'NPO', 'HOL', 'FNS', 
'EXT', 'FND', 'VEN', 'GOV'}

def graph_generation(timeframe=None):
    if type(timeframe) == list:
        timeframe = eval(timeframe)
    elif type(timeframe) == str:
        timeframe = int(timeframe)
    data = pd.read_csv("../data/globalchain.csv")
    G = nx.Graph()
    # countries = set()
    # types = set()
    countries_grouping = {}
    types_grouping = {}
    for country in countries:
        countries_grouping[country] = set()
    for company_type in types:
        types_grouping[company_type] = set()

    for i, row in data.iterrows():
        print(f"\rNodes counted: {i}", end="")
        # Add supplier company if it doesn't exist already. 
        s_id = row["Source"] # (supplier_id)
        c_id = row["Target"] # (supplier id)
        start = row["start_"]
        end = row["end_"]
        transaction_info = [s_id, c_id, start, end]
        if timeframe:
            if type(timeframe) == list:
                if start <= timeframe[0] or end >= timeframe[1]:
                    continue
            else:
                if start >= timeframe or end <= timeframe:
                    continue
        if s_id not in G.nodes():
            # countries.add(row["s_country"])
            # types.add(row["s_entity_type"])
            countries_grouping[str(row["s_country"])].add(s_id)
            types_grouping[str(row["s_entity_type"])].add(s_id)
            # Add supplier node to graph. 
            G.add_node(s_id, id=s_id,
                wrds_id= row["s_fsym_id"],
                name= row["s_name"],
                country= row["s_country"],
                company_type= row["s_entity_type"],
                cusip=row["s_cusip"],
                isin=row["s_isin"],
                sedol=row["s_sedol"],
                ticker=row["s_ticker"],
                recieved_transactions= {},
                sent_transactions= {},
            )
            # print(G.nodes())
        # Add transaction info to supplier node.
        G.nodes[s_id]["sent_transactions"][len(G.nodes[s_id]["sent_transactions"])] = (transaction_info)
        # Add customer company if it doesn't exist already. 
        if c_id not in G.nodes():
            # countries.add(row["c_country"])
            # types.add(row["c_entity_type"])
            countries_grouping[str(row["c_country"])].add(c_id)
            # print(row["c_entity_type"])
            # print(type(row["c_entity_type"]), "type")
            types_grouping[str(row["c_entity_type"])].add(c_id)
            # Add supplier node to graph. 
            G.add_node(c_id, id= c_id,
                wrds_id= row["c_fsym_id"],
                name= row["c_name"],
                country= row["c_country"],
                company_type= row["c_entity_type"],
                cusip=row["c_cusip"],
                isin=row["c_isin"],
                sedol=row["c_sedol"],
                ticker=row["c_ticker"],
                recieved_transactions= {},
                sent_transactions= {},
            )
        # Add transaction info to customer node. 
        G.nodes[c_id]["recieved_transactions"][len(G.nodes[s_id]["recieved_transactions"])] = (transaction_info)

        if not G.has_edge(s_id, c_id):
            G.add_edge(s_id, c_id, supplier=s_id, customer=c_id, history={0 : transaction_info}, transaction_num = 1)  
        # G[s_id][c_id]["history"][len(G[s_id][c_id]["history"])] = transaction_info
        G[s_id][c_id]["transaction_num"] = len(G[s_id][c_id]["history"])
        
    for country in countries_grouping:
        countries_grouping[country] = list(countries_grouping[country])
    for company_type in types_grouping:
        types_grouping[company_type] = list(types_grouping[company_type])
    # try:
    # nx.write_gexf(G, root_dir+"/data/sussy.gexf")
    if timeframe:
        nx.write_gexf(G, root_dir+f"/data/{str(timeframe)}/complete_graph.gexf")
        with open(root_dir+f"/data/{str(timeframe)}/countries_filter.json", "w") as f:
            json.dump(dict(countries_grouping), f)
        with open(root_dir+f"/data/{str(timeframe)}/types_filter.json", "w") as f:
            json.dump(dict(types_grouping), f)
    else:
        nx.write_gexf(G, root_dir+"/data/complete_graph.gexf")
        with open(root_dir+"/data/countries_filter.json", "w") as f:
            json.dump(dict(countries_grouping), f)
        with open(root_dir+"/data/types_filter.json", "w") as f:
            json.dump(dict(types_grouping), f)
    # except Exception as e:
        # print(e)
        # nx.write_gexf(G, "./complete_graph.gexf")
    # nx.write_gexf(G, "../data/sussy.gexf")
    print(f"Nodes: {len(G.nodes)}")
    print(f"Edges: {len(G.edges)}")
    return G


def filter_graphs(filter_type, timeframe, mode, group=None):
    filters = []
    if timeframe == "all":
        G = nx.read_gexf(root_dir+f"/data/complete_graph.gexf")
        # Retrieve filters from data
        if "countries" in filter_type:
            with open("../data/countries_filter.json", "r") as f:
                countries_grouping = json.load(f)
                filters.append(countries_grouping)
        if "types" in filter_type:
            with open("../data/types_filter.json", "r") as f:
                types_grouping = json.load(f)
                filters.append(types_grouping)
    else:
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/complete_graph.gexf")
        # Retrieve filters from data
        if "countries" in filter_type:
            with open(f"../data/{timeframe}/countries_filter.json", "r") as f:
                countries_grouping = json.load(f)
                filters.append(countries_grouping)
        if "types" in filter_type:
            with open(f"../data/{timeframe}/types_filter.json", "r") as f:
                types_grouping = json.load(f)
                filters.append(types_grouping)
    # if "none" in filter_type: (deprecieated)
    #     filters.append({"all": list(G.nodes)})
    #     group = "all"
    # TODO: implement filter intersection of multiple filters later
    # if len(filters) > 1:
    filter = filters[0]
    print("filters loaded")
    # filtered_graph (FG)
    graph_nodes = G.nodes(data=True)
    # print(graph_nodes['0C0C9Y-E'])
    # print(graph_nodes)    
    FG = nx.DiGraph()
    print("new graph created")
    if len(list(filter.keys())) == 1:
        grouping_combinations = itertools.permutations(list(filter.values())[0], 2)
    else:
        grouping_combinations = itertools.permutations(filter.keys(), 2)
    # APPARENTLY PRINTING A LIST OF GROUPING COMBINATIONS EXHAUSTS THEM?? idk
    # print(list(grouping_combinations))
    # print(len(filter.keys()))
    # print(('AW', 'MX') in list(grouping_combinations))
    # print(list(grouping_combinations), "grouping permutations created")
    links_to_transactions = {}
    for permutation in grouping_combinations:
        # print("YO")
        # if G.has_edge(permutation[0], permutation[1]):
        links_to_transactions[(permutation[0], permutation[1])] = {}
    del grouping_combinations
    print("permutations added")
    # Analyze graph within a specific grouping
    if mode == "within":
        group_ids = filter[group]
        # Add nodes from just the group
        # filtered_group_nodes = []
        # for node in group_ids:
            # filtered_group_nodes.append((node, graph_nodes[node]))
            # filtered_group_nodes.append(node)
        # print(filtered_group_nodes)
        # FG.add_nodes_from(filtered_group_nodes)
        FG.add_nodes_from(group_ids)
        # del filtered_group_nodes
        # for node in group_ids:
            # del FG.nodes[node]["sent_transactions"]
            # del FG.nodes[node]["recieved_transactions"]
            # FG.nodes[node]["sent_transactions"] = {}
            # FG.nodes[node]["recieved_transactions"] = {}
        print("filtered nodes added")
        # Add edges, but only if both nodes are in group
        i = 0
        for company_id in group_ids:
            if not G.has_node(company_id):
                continue
            for transaction_info in eval(graph_nodes[company_id]["sent_transactions"]).values():
                supplier = transaction_info[0]
                customer = transaction_info[1]
                transactions_dict = links_to_transactions[(supplier, customer)]
                i += 1
                print(f"\rEdges done: {i}/{len(G.edges)}", end="")
                # print(data)
                if "none" in filter_type or customer.country == group:
                    # If the timeframe is all, take all transactions, otherwise filter
                    # by timeframe (only transactions taking place at that time)
                    if timeframe == "all":
                        transactions_dict[len(transactions_dict)] = transaction_info
                        # FG.nodes[supplier]["sup"]
                        # FG.add_edge(supplier, customer, transaction_num=data["transaction_num"])
                    else:
                        # filtered_history = {}
                        # filtered_transaction_num = 0
                        # if timeframe is a range, take all transactions within that range
                        if type(timeframe) == list:
                            if transaction_info[2] >= timeframe[0] and transaction_info[3] <= timeframe[1]:
                                # filtered_history[key] = transaction_info
                                # filtered_transaction_num += 1
                                transactions_dict[len(transactions_dict)] = transaction_info
                        else:
                        # if timeframe is a point in time, take all transactions occuring then
                            if transaction_info[2] <= timeframe and transaction_info[3] >= timeframe:
                                # filtered_history[key] = transaction_info
                                transactions_dict[len(transactions_dict)] = transaction_info
                                # filtered_transaction_num += 1
                        # FG.add_edge(supplier, customer, history=filtered_history, transaction_num=len(filtered_history))
                        # FG.add_edge(supplier, customer, transaction_num=filtered_transaction_num)
                del supplier, transaction_info, customer
        for link, transactions in links_to_transactions.items():
            if len(transactions) > 0:
                # FG.add_edge(link[0], link[1], history=transactions, transaction_num=len(transactions))
                FG.add_edge(link[0], link[1], transaction_num=len(transactions))
    # Analyze relationships between groupings
    elif mode == "between":
        # Add nodes of groupings
        reverse_filter = {}
        for grouping, group_ids in filter.items():
            # FG.add_node(grouping, sent_transactions={}, recieved_transactions={})
            FG.add_node(grouping)
            # Create reverse lookup table from company id back to grouping
            for company_id in group_ids:
                if '000Y55-E' == company_id:
                    print("CAUGHT!")
                reverse_filter[company_id] = grouping
        print("filtered nodes added")
        # Now go through edges
        i = 0
        for grouping, group_ids in filter.items():
            i += 1
            print(f"\rCurrently on: {i}/{len(filter)} groups", end="")
            for company_id in group_ids:
                if not G.has_node(company_id):
                    continue
                if company_id == '000Y55-E':
                    print(reverse_filter[company_id])
                for transaction_info in eval(graph_nodes[company_id]["sent_transactions"]).values():
                    # If the customer is not in the group, then we are good to go
                    other_grouping = reverse_filter[transaction_info[1]]
                    if other_grouping != grouping:
                        # sent_dict = FG.nodes[grouping]["sent_transactions"]
                        # recieved_dict = FG.nodes[other_grouping]["recieved_transactions"]
                        transactions_dict = links_to_transactions[(grouping, other_grouping)]
                        if timeframe == "all":
                            transactions_dict[len(transactions_dict)] = transaction_info
                            # sent_dict[len(sent_dict)] = transaction_info
                            # recieved_dict[len(recieved_dict)] = transaction_info
                        else:
                            if type(timeframe) == list:
                                if transaction_info[2] >= timeframe[0] and transaction_info[3] <= timeframe[1]:
                                    transactions_dict[len(transactions_dict)] = transaction_info
                                    # sent_dict[len(sent_dict)] = transaction_info
                                    # recieved_dict[len(recieved_dict)] = transaction_info
                                # else:
                                    # print("HTINGS ARE GETTING DROPPED", transaction_info)
                            else:
                            # if timeframe is a point in time, take all transactions occuring then
                                if transaction_info[2] <= int(timeframe) and transaction_info[3] >= int(timeframe):
                                    transactions_dict[len(transactions_dict)] = transaction_info
                                    # sent_dict[len(sent_dict)] = transaction_info
                                    # recieved_dict[len(recieved_dict)] = transaction_info
        for link, transactions in links_to_transactions.items():
            if len(transactions) > 0:
                # FG.add_edge(link[0], link[1], history=transactions, transaction_num=len(transactions))
                FG.add_edge(link[0], link[1], transaction_num=len(transactions))
    else:
        raise Exception("Incorrect mode!")
    # try:
    if timeframe:
        nx.write_gexf(FG, root_dir+f"/data/{str(timeframe)}_{mode}_{filter_type}_filtered_graph.gexf")
    else:
        nx.write_gexf(FG, root_dir+f"/data/{str(timeframe)}_{mode}_{filter_type}_filtered_graph.gexf")
    # except FileNotFoundError:
        # nx.write_gexf(FG, root_dir+f"./{filter_type}_filtered_graph.gexf")
    print("")
    print(f"Nodes: {len(FG.nodes)}")
    print(f"Edges: {len(FG.edges)}")
    

if __name__ =="__main__":
    function = sys.argv[1]
    if function == "generation":
        if len(sys.argv) > 2:
            timeframe = sys.argv[2] 
            _ = graph_generation(timeframe)
        else:
            _ = graph_generation()
    elif function == "filter":
        filter = sys.argv[2]
        timeframe = sys.argv[3]
        mode = sys.argv[4]
        if len(sys.argv) > 5:
            group = sys.argv[5]
            filter_graphs(filter, timeframe, mode, group)
        else:
            filter_graphs(filter, timeframe, mode)
        # try:
        # except FileNotFoundError:
            # G = nx.read_gexf(root_dir+"/complete_graph.gexf")
        # filter_graphs(G, "countries", [21900, 21960], "between")
        print("full graph read!")
        # filter_graphs(G, "countries", 22000, "between")
        # filter_graphs(G, "countries", 22100, "between")
        # filter_graphs(G, "types", "all", "between")
        # filter_graphs(G, "countries", 22100, "between")
        # filter_graphs(G, filter_type="none", timeframe=22100, mode="within", group="all")
        # filter_graphs(G, filter_type="types", timeframe=22200, mode="between")
        # filter_graphs(G, "countries", "all", "within", "JPN")
    # if not os.path.isfile(root_dir+"/data/complete_graph.gexf"):
        # _ = graph_generation()