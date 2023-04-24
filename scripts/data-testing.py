import networkx as nx
import pandas as pd
import numpy as np
import os
import sys
import json
import itertools
import pathlib
import matplotlib.pyplot as plt
root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
# with open(root_dir+"/data/complete_graph.gexf", "r") as f:
    # print("THIS WORKS")
# from classes import *
countries = ("nan", 'Bosnia and Herzegovina', 'Madagascar', 'Israel', 'Uzbekistan', 'Bahamas', 'Tunisia', 'Togo', 
'Bermuda', 'Italy', 'Hong Kong', 'Morocco', 'Bolivia', 'Qatar', 'Solomon Islands', 'Puerto Rico', 'Ecuador', 
'Mauritania', 'British Virgin Islands', 'Bahrain', 'Malta', 'Belgium', 'Iraq', 'Cyprus', 'Faroe Islands', 'Benin', 
'Monaco', 'New Zealand', 'Jamaica', 'Denmark', 'Tanzania', 'Vietnam', 'Algeria', 'Chile', 'Serbia', 'Macau', 
'United Arab Emirates', 'Panama', 'Dominica', 'Lithuania', 'Lebanon', 'China', 'South Sudan', 'Honduras', 
'Czech Republic', 'Guinea', 'Netherlands Antilles', 'United Kingdom', 'Costa Rica', 'Barbados', 'Poland', 'Guyana', 
'Austria', 'Haiti', 'Congo (Dem. Rep. of the)', 'Libya', 'Estonia', 'Antigua and Barbuda', 'Aruba', 'Iran', 'Angola',
 'Latvia', 'Portugal', 'Nepal', 'Liechtenstein', 'Kosovo', 'Mongolia', 'Nigeria', 'Peru', 'Norway', 'Niger', 'Kenya',
  'Malawi', 'Cuba', 'Gambia', 'Mali', 'Saint Kitts and Nevis', 'Supranational', 'Aland Islands', 'Egypt', 'Taiwan',
   'Anguilla', 'Greenland', 'Canada', 'Oman', 'Mexico', 'Moldova', 'Georgia', 'Greece', 'Pakistan', 
   'Russian Federation', 'French Polynesia', 'United States', 'American Samoa', 'Finland', 'South Africa',
    'Indonesia', 'Tajikistan', 'Bangladesh', 'Jordan', 'Kyrgyzstan', 'Gibraltar', 'Burundi', 'Spain', 'Brazil', 
    'Swaziland', 'Djibouti', 'Namibia', 'Montenegro', 'Belarus', 'Cayman Islands', 'Botswana', 'Malaysia', 
    'Nicaragua', 'Myanmar', 'Rwanda', 'Venezuela', 'Bulgaria', 'Marshall Islands', 'Australia', 'Macedonia', 
    'Senegal', 'Gabon', 'Albania', 'Liberia', 'Iceland', 'Germany', 'Cape Verde', 'El Salvador', 'Netherlands', 
    'Mozambique', 'Singapore', 'Sierra Leone', 'Belize', 'Croatia', 'Laos', 'Armenia', 'Timor-Leste', 'France',
     'Cameroon', 'Sao Tome and Principe', 'Uganda', 'Turkey', 'Equatorial Guinea', 'Uruguay', 'Romania', 'India', 
     'Guatemala', 'Ukraine', 'Azerbaijan', 'Ivory Coast', 'Paraguay', 'Argentina', 'Colombia', 'Saudi Arabia', 
     'San Marino', 'Luxembourg', 'North Korea', 'Guam', 'Ethiopia', 'Ireland', 'Martinique', 'Papua New Guinea', 
     'New Caledonia', 'Maldives', 'Philippines', 'Switzerland', 'Hungary', 'Dominican Republic', 'Vatican City', 
     'Sri Lanka', 'Sudan', 'Brunei', 'Samoa', 'Trinidad and Tobago', 'Seychelles', 'Suriname', 'Palestine', 'Japan',
      'South Korea', 'Kazakhstan', 'Mauritius', 'Ghana', 'Sweden', 'Yemen', 'Kuwait', 'Turkmenistan', 'Cambodia', 
      'Tuvalu', 'Afghanistan', 'Kiribati', 'Bhutan', 'Thailand', 'Zimbabwe', 'Slovenia', 'Burkina Faso', 'Zambia', 
      'Vanuatu', 'Slovakia', 'Fiji', 'Syria', 'U.S. Virgin Islands', 'La Reunion', 'Micronesia', 'Congo (Rep. of)',
      'Somalia', 'Andorra', 'Tonga', 'Comoros', 'Palau', 'St Vincent & Grenadines', 'St. Lucia', 'Chad', 'Eritrea',
      'Central African Republic')

types = ("nan", 'CAC', 'SHP', 'OPD', 'PEF', 'ESP', 'PVT', 'PVF', 'TRU', 'SOV', 'PRO', 'COL', 'BRA', 'FAF', 'JVT', 
'SUB', 'HED', 'MUT', 'COR', 'UMB', 'PRT', 'UIT', 'MED', 'MUE', 'BAS', 'PUB', 'ABS', 'MUC', 'NPO', 'HOL', 'FNS', 
'EXT', 'FND', 'VEN', 'GOV')

def graph_generation(timeframe=None):
    if type(timeframe) == list:
        timeframe = eval(timeframe)
    elif type(timeframe) == str:
        date = pd.to_datetime(int(timeframe), origin='1960-01-01', unit='D')
        print(f"Date: {date}")
        timeframe = int(timeframe)
    # data = pd.read_csv("../data/globalchain.csv")
    data = pd.read_csv("data/globalchain.csv")
    G = nx.DiGraph()
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
            # countries.add(row["fs_s_country"])
            if str(row["fs_s_country"]) not in countries_grouping:
                countries_grouping[str(row["fs_s_country"])] = set()
                print(str(row["fs_c_country"]))
            # types.add(row["s_entity_type"])
            countries_grouping[str(row["fs_s_country"])].add(s_id)
            types_grouping[str(row["s_entity_type"])].add(s_id)
            # Add supplier node to graph. 
            G.add_node(s_id, id=s_id,
                wrds_id= row["s_fsym_id"],
                name= row["s_name"],
                country= row["fs_s_country"],
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
            # countries.add(row["fs_c_country"])
            if str(row["fs_c_country"]) not in countries_grouping:
                countries_grouping[str(row["fs_c_country"])] = set()
                print(str(row["fs_c_country"]))
            # types.add(row["c_entity_type"])
            countries_grouping[str(row["fs_c_country"])].add(c_id)
            # print(row["c_entity_type"])
            # print(type(row["c_entity_type"]), "type")
            types_grouping[str(row["c_entity_type"])].add(c_id)
            # Add supplier node to graph. 
            G.add_node(c_id, id= c_id,
                wrds_id= row["c_fsym_id"],
                name= row["c_name"],
                country= row["fs_c_country"],
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
        if not os.path.exists(root_dir+f"/data/{str(timeframe)}/"):
            os.mkdir(root_dir+f"/data/{str(timeframe)}/")
        nx.write_gexf(G, root_dir+f"/data/{str(timeframe)}/{str(timeframe)}_complete_graph.gexf")
        with open(root_dir+f"/data/{str(timeframe)}/{str(timeframe)}_countries_filter.json", "w") as f:
            json.dump(dict(countries_grouping), f)
        with open(root_dir+f"/data/{str(timeframe)}/{str(timeframe)}_types_filter.json", "w") as f:
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
    print("")
    print(f"Nodes: {len(G.nodes)}")
    print(f"Edges: {len(G.edges)}")
    # print(countries)
    return G


def filter_graph(filter_type, timeframe, mode, group=None):
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
        date = pd.to_datetime(int(timeframe), origin='1960-01-01', unit='D')
        print(f"Date: {date}")
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{str(timeframe)}_complete_graph.gexf")
        # Retrieve filters from data
        if "countries" in filter_type:
            with open(f"../data/{timeframe}/{str(timeframe)}_countries_filter.json", "r") as f:
                countries_grouping = json.load(f)
                filters.append(countries_grouping)
        if "types" in filter_type:
            with open(f"../data/{timeframe}/{str(timeframe)}_types_filter.json", "r") as f:
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
        nx.write_gexf(FG, root_dir+f"/data/{str(timeframe)}/{str(timeframe)}_{mode}_{filter_type}_filtered_graph.gexf")
    else:
        nx.write_gexf(FG, root_dir+f"/data/{mode}_{filter_type}_filtered_graph.gexf")
    # except FileNotFoundError:
        # nx.write_gexf(FG, root_dir+f"./{filter_type}_filtered_graph.gexf")
    print("")
    print(f"Nodes: {len(FG.nodes)}")
    print(f"Edges: {len(FG.edges)}")
    

def analyze_graph(timeframe, filter=None):
    if timeframe == "all":
        G = nx.read_gexf(root_dir+f"/data/complete_graph.gexf")
        if "countries" == filter:
            with open(root_dir+"/data/countries_filter.json", "r") as f:
                countries_grouping = json.load(f)
                filter = countries_grouping
        elif "types" == filter:
            with open(root_dir+"/data/types_filter.json", "r") as f:
                types_grouping = json.load(f)
                filter = types_grouping
    else:
        date = pd.to_datetime(int(timeframe), origin='1960-01-01', unit='D')
        print(f"Date: {date}")
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{timeframe}_complete_graph.gexf")
        if "countries" == filter:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_countries_filter.json", "r") as f:
                countries_grouping = json.load(f)
                filter = countries_grouping
        elif "types" == filter:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_types_filter.json", "r") as f:
                types_grouping = json.load(f)
                filter = types_grouping
    if filter:
        print("OK!")
        top_groups = sorted(filter.items(), key=lambda x:len(x[1]))
        for group_tuple in top_groups:
            group = group_tuple[0]
            grouping = filter[group]
            if len(grouping) == 0:
                continue
            node_degrees = {}
            degree_sum = 0
            in_degree = 0
            out_degree = 0
            node_total = len(grouping)
            for i, node in enumerate(grouping):
                print(f"\rNode {i}/{node_total}", end="")
                degree = len(list(G.neighbors(node)))
                node_degrees[G.nodes[node]["name"]]  = degree
                degree_sum += degree
                in_degree += G.in_degree(node)
                out_degree += G.out_degree(node)
            print("")
            top_degrees = sorted(node_degrees.items(), key=lambda x:x[1], reverse=True)
            print(f"{group} Top companies: {top_degrees[:5]}")
            print(f"{group} Average degree: {degree_sum/node_total}")
            print(f"{group} Number of companies: {node_total}")
            print(f"Export percentage: {round(out_degree/(in_degree+out_degree), 3)}")
    else:
        node_degrees = {}
        degree_sum = 0
        node_total = len(G.nodes)
        in_degree = 0
        out_degree = 0
        for i, node in enumerate(G.nodes):
            # print(node)
            print(f"\rNode {i}/{node_total}", end="")
            degree = len(list(G.neighbors(node)))
            # print(list(G.neighbors(node)))
            # print(G.degree(node))
            # print(degree)
            node_degrees[G.nodes[node]["name"]]  = degree
            # degree_sum += degree
            degree_sum += degree
            in_degree += G.in_degree(node)
            out_degree += G.out_degree(node)
        print("")
        top_degrees = sorted(node_degrees.items(), key=lambda x:x[1], reverse=True)
        print(f"Top companies: {top_degrees[:30]}")
        print(f"Average degree: {degree_sum/node_total}")
        print(f"Export percentage: {round(out_degree/(in_degree+out_degree), 3)}")
        print(out_degree, in_degree)
    plt.hist(node_degrees.values(), bins=50)
    plt.savefig("degree_plot.png")

if __name__ =="__main__":
    function = sys.argv[1]
    if function == "generate":
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
            filter_graph(filter, timeframe, mode, group)
        else:
            filter_graph(filter, timeframe, mode)
    elif function == "analyze":
        timeframe = sys.argv[2]
        if len(sys.argv) > 3:
            filter = sys.argv[3]
            analyze_graph(timeframe, filter)
        else:
            analyze_graph(timeframe)
        # try:
        # except FileNotFoundError:
            # G = nx.read_gexf(root_dir+"/complete_graph.gexf")
        # filter_graph(G, "countries", [21900, 21960], "between")
        # print("full graph read!")
        # filter_graph(G, "countries", 22000, "between")
        # filter_graph(G, "countries", 22100, "between")
        # filter_graph(G, "types", "all", "between")
        # filter_graph(G, "countries", 22100, "between")
        # filter_graph(G, filter_type="none", timeframe=22100, mode="within", group="all")
        # filter_graph(G, filter_type="types", timeframe=22200, mode="between")
        # filter_graph(G, "countries", "all", "within", "JPN")
    # if not os.path.isfile(root_dir+"/data/complete_graph.gexf"):
        # _ = graph_generation()