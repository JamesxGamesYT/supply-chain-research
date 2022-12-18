import sys
import json
import os
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


# This data comes from https://ourworldindata.org/policy-responses-covid
def covid_analysis(timeframe):
    data = pd.read_csv("../data/covid-containment-and-health-index.csv", )
    data = data.groupby(['Entity'])
    date = pd.to_datetime(int(timeframe), origin='1960-01-01', unit='D')
    print(f"Date: {date}")
    # baseline_containment_indices = {}
    containment_indices = {}
    for name, group in data:
        group["Day"] = pd.to_datetime(group["Day"])
        entry = group[group["Day"] == date]
        try:
            index = entry["containment_index"].values[0]
            containment_indices[name] = index
        except:
            pass
        # baseline_containment_indices[name] = 
        # baseline_index = group[group["Day"] == "2022-1-16"]["containment_index"].values[0]
            # print(name, entry)
        # print(index, type(index))
    # print(containment_indices)
        # date_range = pd._date_r   ange(start="1/1/2020", end="12/8/2022",freq="D")
        # pd.fillna
    # print(date)
    # print(date.year)
    baseline_G = nx.read_gexf(f"../data/21870/21870_complete_graph.gexf")
    with open(f"../data/21870/21870_countries_filter.json", "r") as f:
        baseline_countries_grouping = json.load(f)
    baseline_countries_info = {}
    for country, company_list in baseline_countries_grouping.items():
        if country not in containment_indices:
            continue
        if len(company_list) == 0:
            continue
        degree_sum = 0 
        in_degree = 0
        out_degree = 0
        for company in company_list:
            try:
                degree_sum += int(baseline_G.degree(company))
            except TypeError:
                print(company)
                print(company_list, country)
            in_degree += baseline_G.in_degree(company)
            out_degree += baseline_G.out_degree(company)
        baseline_countries_info[country] = degree_sum/len(company_list)
        # baseline_countries_info[country] = degree_sum
    G = nx.read_gexf(f"../data/{timeframe}/{str(timeframe)}_complete_graph.gexf")
    with open(f"../data/{timeframe}/{str(timeframe)}_countries_filter.json", "r") as f:
        countries_grouping = json.load(f)
    countries_info = {}
    for country, company_list in countries_grouping.items():
        if country not in containment_indices:
            continue
        if len(company_list) == 0:
            continue
        degree_sum = 0 
        in_degree = 0
        out_degree = 0
        for company in company_list:
            degree_sum += G.degree(company)
            in_degree += G.in_degree(company)
            out_degree += G.out_degree(company)
        # countries_info[country] = degree_sum
        countries_info[country] = degree_sum/len(company_list)

    countries_to_drop = []
    for country in containment_indices:
        if country not in countries_info or country not in baseline_countries_info:
            countries_to_drop.append(country)
    for country in countries_to_drop:
        del containment_indices[country]
    containment_values = []
    degree_values = []
    for country in containment_indices:
        containment_values.append(containment_indices[country])
        # degree_values.append(countries_info[country])
        print(country, baseline_countries_info[country] - countries_info[country])
        degree_values.append(baseline_countries_info[country] - countries_info[country])
        # plt.scatter(containment_indices[country], countries_info[country])
        # plt.scatter(containment_indices[country], baseline_countries_info[country])
        # plt.scatter(containment_indices[country], (baseline_countries_info[country] - countries_info[country])/baseline_countries_info[country])
        plt.scatter(containment_indices[country], (baseline_countries_info[country] - countries_info[country]))
    z = np.polyfit(containment_values, degree_values, 1)
    p = np.poly1d(z)
    print(z, p)
    print(sum(degree_values)/len(degree_values))
    # plt.plot(containment_values, p(containment_values), "r-")
    # plt.scatter(containment_indices.values(), countries_info.values())
    # plt.scatter(containment_indices.values(), countries_info.values())
    # for i, name in enumerate(containment_indices):
        # plt.annotate(name, (containment_indices[name],countries_info[name]))
        # plt.annotate(name, (containment_indices[name],baseline_countries_info[name] - countries_info[name]))
    plt.savefig("testing.png")
        
if __name__ =="__main__":
    timeframe = sys.argv[1]
    covid_analysis(timeframe)