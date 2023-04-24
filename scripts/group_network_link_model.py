import sys
import os
import json
import scipy.stats
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

# Expands upon the filter_graph function in data testing
def create_network_data(grouping, timeframes):
    """
    Generates network and efficiency data for the company lists of each of the groupings by timeframe
    """
    # Keys are timeframes, values are dictionary of keys being a group and the values being a dictionary of a group 
    # and the num of connections to the first group
    efficiency_data = {}
    network_data = {}
    for i, timeframe in enumerate(timeframes):
        print(f"\r{i}/{len(timeframes)}", end="\n")
        timeframe_efficiency_dict = {}
        timeframe_network_dict = {}
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{timeframe}_complete_graph.gexf")
        # TODO: maybe intersect certain groupings?
        if "countries" == grouping:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_countries_filter.json", "r") as f:
                filter = json.load(f)
        elif "types" == grouping:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_types_filter.json", "r") as f:
                filter = json.load(f)
        reverse_filter = {}
        for group, company_list in filter.items():
            # Create reverse lookup table from company id back to grouping
            for company_id in company_list:
                reverse_filter[company_id] = group
        for group, company_list in filter.items():
            if len(company_list) == 0:
                continue
            efficiency = nx.local_efficiency(G.subgraph(company_list).to_undirected())
            group_dict = {other_group : 0 for other_group in filter}
            for company in company_list:
                neighbors = G.neighbors(company)
                for neighbor in neighbors:
                    other_grouping = reverse_filter[neighbor]
                    group_dict[other_grouping] += 1
            timeframe_network_dict[group] = group_dict
            timeframe_efficiency_dict[group] = efficiency
        network_data[timeframe] = timeframe_network_dict
        efficiency_data[timeframe] = timeframe_efficiency_dict
    # IF NECESSARY, DROP IT INTO A FILE
    with open(f"{timeframes[0]}-{timeframes[-1]}_network_data.json", 'w') as f:
        json.dump(network_data, f)
    with open(f"{timeframes[0]}-{timeframes[-1]}_efficiency_data.json", 'w') as f:
        json.dump(efficiency_data, f)
    return network_data, efficiency_data

def calculate_network_exposures(grouping, timeframes):
    """
    Using network data, calculates exposures. FOR EXPORTS
    # EXPOSURE: exposure of a group to another group is the correlation between changes in the intra vs. inter group
    # times the recirpocal of the fraction of the inter group to the overall companies in that group
    """
    # Reformat data by group
    # Just a list of the groups, no company lists attached
    with open(f"{timeframes[0]}-{timeframes[-1]}_network_data.json", 'r') as f:
        network_data = json.load(f)
    for i, timeframe in enumerate(timeframes):
        if "countries" == grouping:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_countries_filter.json", "r") as f:
                filter = json.load(f)
        elif "types" == grouping:
            with open(root_dir+f"/data/{timeframe}/{timeframe}_types_filter.json", "r") as f:
                filter = json.load(f)
        groups_to_drop = []
        for group, company_list in filter.items():
            if len(company_list) == 0:
                groups_to_drop.append(group)
        for group in groups_to_drop:
            del filter[group]
        if i == 0:
            intersected_filter = set(filter.keys())
        else:
            intersected_filter = intersected_filter.intersection(set(filter.keys()))
    exposure_matrix = {}
    # Remove groups without enough links
    groups_to_drop = set()
    for group in intersected_filter:
        drop = False
        for timeframe in timeframes:
            total_links = sum([x for x in network_data[timeframe][group].values()])
            if total_links < 10:
                drop = True
                break
        if drop:
            groups_to_drop.add(group)
    intersected_filter = intersected_filter.difference(groups_to_drop)

    for group in intersected_filter:
        total_intensities = {other_group : 0 for other_group in intersected_filter}
        country_correlation_x = {other_group: [] for other_group in intersected_filter}
        country_correlation_y = {other_group: [] for other_group in intersected_filter}
        total_correlations = {other_group : 0 for other_group in intersected_filter}
        for i, timeframe in enumerate(timeframes):
            total_links = sum([x for x in network_data[timeframe][group].values()])
            # current_intensities = {other_group : value/total_links for other_group, value in network_data[timeframe][group].items()}
            # current_intensities = {other_group : value for other_group, value in network_data[timeframe][group].items()}
            for other_group in intersected_filter:
                # total_intensities[other_group] += current_intensities[other_group]
                intensity = network_data[timeframe][group][other_group]/total_links
                total_intensities[other_group] += intensity

                # Calculate points for correlations
                # x is the normalized change in just that link between the two groups over time
                # Y is the change between within the group, doesn't depend on other group over time
                if i == 0:
                    # baseline_test = (network_data[timeframe][group][other_group],total_links)
                    previous_x = network_data[timeframe][group][other_group]
                    previous_y = total_links
                else:
                    country_correlation_x[other_group].append(
                        # (network_data[timeframe][group][other_group]-previous_x)/previous_x)
                        (network_data[timeframe][group][other_group]-previous_x))
                    previous_x = network_data[timeframe][group][other_group]
                    country_correlation_y[other_group].append(
                        # (total_links-previous_y)/previous_y)
                        (total_links-previous_y))
                    # previous_y = total_links
                # if previous_x or previous_y == 0:

        # Intensity * Correlation = exposure 
        average_intensity = {other_group: total_intensities[other_group]/len(timeframes) for other_group in intersected_filter}
        for other_group in intersected_filter:
            # print((country_correlation_x[other_group], country_correlation_y[other_group]), other_group)
            total_correlations[other_group] = scipy.stats.pearsonr(country_correlation_x[other_group], country_correlation_y[other_group])[0]
            # correlation = scipy.stats.pearsonr(country_correlation_x, country_correlation_y)
        average_exposure = {other_group: average_intensity[other_group]*total_correlations[other_group] for other_group in intersected_filter}
        # if group == "United States":
            # print(total_correlations, average_intensity, average_exposure)
        exposure_matrix[group] = average_exposure
        # exposure_matrix[group] = average_intensity

    # Column: export exposure, row: export exposee/import exposer (NOTE: not normalized from log perspective, can't be compared)
    df = pd.DataFrame.from_dict(exposure_matrix)
    df.index.name = "country"
    df.to_csv(f"{timeframes[0]}-{timeframes[-1]}_test_model_exposures.csv")

    # plt.scatter(country_correlation_x, country_correlation_y)
    # for i, point in enumerate(country_correlation_x):
    #     plt.annotate(timeframes[i+1], (country_correlation_x[i], country_correlation_y[i]))
    # plt.savefig(f"{timeframes[0]}-{timeframes[-1]}_correlation_test.png")

def compare_exposures():
    """
    Given a matrix of 
    """
    initial_df = pd.read_csv("21870-21870_test_model_exposures.csv", index_col="country")
    final_df = pd.read_csv("21870-22370_test_model_exposures.csv", index_col="country")
    common_groups   = initial_df.index.intersection(final_df.index)
    initial_df = initial_df.loc[common_groups, common_groups]
    final_df = final_df.loc[common_groups, common_groups]
    difference_df = final_df - initial_df
    difference_df.to_csv("21870-22370_test_difference_exposures.csv")

def summary_statistics(timeframe):
    df = pd.read_csv(f"{timeframe}-{timeframe}_test_model_exposures.csv", index_col="country")
    exposure_index = pd.Series(index=df.index)
    # Uses herfindal index
    export_concentration_index = pd.Series(index=df.index).fillna(0)
    import_concentration_index = pd.Series(index=df.index).fillna(0)
    for group in df.index:
        exposure_index[group] = 1 - df.loc[group, group]
        for other_group in df.index:
            if group == other_group:
                continue
            export_exposure = df.loc[other_group, group]
            import_exposure = df.loc[group, other_group]
            total_exposure = exposure_index[group]
            export_concentration_index[group] += 10000*(export_exposure/total_exposure)**2   
            import_concentration_index[group] += 10000*(import_exposure/total_exposure)**2
    with open(f"{timeframe}-{timeframe}_efficiency_data.json", "r") as f:
        efficiency_data = json.load(f)

if __name__ == "__main__":
    grouping = sys.argv[1]
    timeframe = sys.argv[2]
    if timeframe == "2008":
        timeframes = ["17540", "17620", "17720", "17820", "18020", "18120", "18220", "18320", "18420", "18520", "18620", "18720", "18820", "18920", "19020", "19120", "19220", "19320", "19420", "19520"]
        # timeframes = ["17540"]
        # timeframes = ["21870"]
    if timeframe == "covid":
        timeframes = ["21870", "21930", "21960", "22000", "22100", "22200", "22300", "22370"]
    # network_data = create_network_data(grouping, timeframes)
    calculate_network_exposures(grouping, timeframes)
    # compare_exposures()