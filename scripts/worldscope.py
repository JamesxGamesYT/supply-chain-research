import pandas as pd
from collections import defaultdict
import networkx as nx
import os
import json

root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def extract_columns():
    df = pd.read_csv("wrds_ws_funda_new.csv")
    df = df[[
        "ITEM7230", # Business metrics
        "ITEM7250",
        "ITEM7240",
        "ITEM2301",
        "ITEM7210",
        "ITEM7220",
        "ITEM7240",
        "ITEM8236",
        "ITEM8416",
        "ITEM8341",
        "ITEM8601",
        "ITEM7210",
        "ITEM7220",
        "ITEM7240",
        "ITEM7250",
        "ITEM5601", # Ticker
        "ITEM6004", # CUSIP
        "ITEM6006", # Sedol
        "ITEM6008", # Isin
        "ITEM6035", # Worldscope ID
        "ITEM6105", # Permanent ID 
        "year_"]
    ]
    df.to_csv("extracted_worldscope.csv")

def match_to_globalchain():
    worldscope = pd.read_csv("extracted_worldscope.csv", index_col="INDEX")
    # ticker_to_lines = defaultdict(list)
    # cusip_to_lines = defaultdict(list)
    # sedol_to_lines = defaultdict(list)
    # isin_to_lines = defaultdict(list)
    # for i, row in worldscope.iterrows():
    #     # if row["year_"] not in years:
    #         # continue
    #     if not pd.isna(row["ITEM5601"]):
    #         # TODO: fix issue where it double counts duplicated rows
    #         ticker_to_lines[row["ITEM5601"]].append(i)
    #     if not pd.isna(row["ITEM6004"]):
    #         cusip_to_lines[row["ITEM6004"]].append(i)
    #     if not pd.isna(row["ITEM6006"]):
    #         sedol_to_lines[row["ITEM6006"]].append(i)
    #     if not pd.isna(row["ITEM6008"]):
    #         isin_to_lines[row["ITEM6008"]].append(i)

    # with open("isin.json", "w") as f:
    #     json.dump(isin_to_lines, f)
    # with open("sedol.json", "w") as f:
    #     json.dump(sedol_to_lines, f)
    # with open("cusip.json", "w") as f:
    #     json.dump(cusip_to_lines, f)
    # with open("ticker.json", "w") as f:
    #     json.dump(ticker_to_lines, f)
    with open("isin.json", "r") as f:
        isin_to_lines = json.load(f)
    with open("sedol.json", "r") as f:
        sedol_to_lines = json.load(f)
    with open("cusip.json", "r") as f:
        cusip_to_lines = json.load(f)
    with open("ticker.json", "r") as f:
        ticker_to_lines = json.load(f)

    print("Worldscope data created")
    nodes_17714 = set(nx.read_gexf(root_dir+f"/data/17714/17714_complete_graph.gexf").nodes)
    nodes_18079 = set(nx.read_gexf(root_dir+f"/data/18079/18079_complete_graph.gexf").nodes)
    nodes_18809 = set(nx.read_gexf(root_dir+f"/data/18809/18809_complete_graph.gexf").nodes)
    all_nodes =  nodes_17714.union(nodes_18079, nodes_18809)
    print(len(all_nodes))
    globalchain = pd.read_csv("data/globalchain.csv")
    # Globalchain ID to row indices for worldscope
    matching = {}
    failed = set()
    for i, row in globalchain.iterrows():
        if row["Source"] not in matching and row["Source"] in all_nodes:
        # if row["Source"] not in matching:
            matching_set = set()
            if row["s_ticker"] in ticker_to_lines.keys():
                matching_set = matching_set.union(set(ticker_to_lines[row["s_ticker"]]))
                # matching[row["Source"]] = ticker_to_lines[row["s_ticker"]]
            if row["s_sedol"] in sedol_to_lines.keys():
                matching_set = matching_set.union(set(sedol_to_lines[row["s_sedol"]]))
                # matching[row["Source"]] = sedol_to_lines[row["s_sedol"]]
            if row["s_isin"] in isin_to_lines.keys():
                matching_set = matching_set.union(set(isin_to_lines[row["s_isin"]]))
                # matching[row["Source"]] = isin_to_lines[row["s_isin"]]
            if row["s_cusip"] in cusip_to_lines.keys():
                matching_set = matching_set.union(set(cusip_to_lines[row["s_cusip"]]))
                # matching[row["Source"]] = cusip_to_lines[row["s_cusip"]]
            if len(matching_set) == 0:
                if row["Source"] not in matching:
                    failed.add(row["Source"])
            else:
                matching[row["Source"]] = matching_set
        if row["Target"] not in matching and row["Target"] in all_nodes:
        # if row["Target"] not in matching:
            matching_set = set()
            if row["c_ticker"] in ticker_to_lines.keys():
                matching_set = matching_set.union(set(ticker_to_lines[row["c_ticker"]]))
                # matching[row["Target"]] = ticker_to_lines[row["c_ticker"]]
            if row["c_sedol"] in sedol_to_lines.keys():
                matching_set = matching_set.union(set(sedol_to_lines[row["c_sedol"]]))
                # matching[row["Target"]] = sedol_to_lines[row["c_sedol"]]
            if row["c_isin"] in isin_to_lines.keys():
                matching_set = matching_set.union(set(isin_to_lines[row["c_isin"]]))
                # matching[row["Target"]] = isin_to_lines[row["c_isin"]]
            if row["c_cusip"] in cusip_to_lines.keys():
                matching_set = matching_set.union(set(cusip_to_lines[row["c_cusip"]]))
                # matching[row["Target"]] = cusip_to_lines[row["c_cusip"]]
            if len(matching_set) == 0:
                if row["Target"] not in matching:
                    failed.add(row["Target"])
                # print(row["Target"], row["c_ticker"], row["c_sedol"], row["c_isin"], row["c_cusip"])
            else:
                matching[row["Target"]] = matching_set
    print(len(matching))
    print(len(failed))
    for match in matching.keys():
        matching[match] = list(matching[match])
    with open("matching_dict.json", "w") as f:
        json.dump(matching, f)
    with open("matching_dict.json", "r") as f:
        matching = json.load(f)
    
    # print(matching)
    # revenue_df = pd.DataFrame(columns=years, index=matching.keys())
    years = [2007, 2008, 2009, 2010, 2011, 2012]
    revenue_dict = {}
    for company, row_indices in matching.items():
        revenues = []
        years_had = []
        for row_index in row_indices:
            # for year in ['2007', '2008', '2009', '2010', '2011', '2012']:
            if worldscope["year_"][row_index] in years and worldscope["year_"][row_index] not in years_had:
                try:
                    revenues.append(worldscope["ITEM7230"][row_index])
                except:
                    revenues.append(None)
                years_had.append(worldscope["year_"][row_index])
        revenue_dict[company] = revenues
    revenue_df = pd.DataFrame.from_dict(revenue_dict, orient='index', columns=years)
                # revenue_df[company, worldscope["year_"][row_index]] = worldscope["ITEM7230"][row_index]
    revenue_df.to_csv("revenue_data.csv")

def revenue_estimation():
    revenue_df = pd.read_csv("revenue_data.csv")
    null = revenue_df[revenue_df["2007"].isnull() == False]
    print(len(null), len(revenue_df))
    null = null[null["2008"].isnull() == False]
    print(len(null), len(revenue_df))
    null = null[null["2009"].isnull() == False]
    print(len(null), len(revenue_df))
    null = null[null["2010"].isnull() == False]
    print(len(null), len(revenue_df))
    null = null[null["2011"].isnull() == False]
    print(len(null), len(revenue_df))

if __name__ == "__main__":
    # match_to_globalchain()
    revenue_estimation()