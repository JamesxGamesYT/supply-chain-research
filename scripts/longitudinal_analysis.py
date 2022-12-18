import sys
import os
import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
root_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def longitudinal_extraction(crisis, grouping):
    """
    Extract longitudinal connection change data for the crisis and grouping/filter in question. 
    """
    if crisis == "2008":
        snapshots = [17540, 17620, 17720, 17820, 18020, 18120, 18220, 18320, 18420, 18520, 18620, 18720, 18820, 18920, 19020, 19120, 19220, 19320, 19420, 19520]
        # snapshots = [17540, 17620]
    if crisis == "covid":
        snapshots = [21870, 21930, 21960, 22000, 22100, 22200, 22300, 22370]
        # snapshots = [21870, 21930]
    degree_data = {}    
    total_average_degrees = {}
    previous_timeframe_connections = {}
    baseline_timeframe_connections = {}
    final_timeframe_connections = {}
    connections_lost = defaultdict(dict)
    connections_gained = defaultdict(dict)
    for i, timeframe in enumerate(snapshots):
        print(f"\r {i}/{len(snapshots)} snapshots")
        G = nx.read_gexf(root_dir+f"/data/{timeframe}/{timeframe}_complete_graph.gexf")
        if "countries" == grouping:
            with open(f"../data/{timeframe}/{timeframe}_countries_filter.json", "r") as f:
                filter = json.load(f)
        elif "types" == grouping:
            with open(f"../data/{timeframe}/{timeframe}_types_filter.json", "r") as f:
                filter = json.load(f)
        elif "companies" == grouping:
            filter = {}
            for node in G.nodes:
                filter[str(node)] = [node]
        snapshot_data = {}
        total_average_degree = 0
        for group, company_list in filter.items():
            if len(company_list) == 0:
                continue
            average_degree = 0
            for company in company_list:
                neighbors = set(G.neighbors(company))
                if company in previous_timeframe_connections:
                    # Compare changes in neighbors (suppliers/customers) over a crisis' time
                    previous_neighbors = previous_timeframe_connections[company]
                    gained = neighbors.difference(previous_neighbors)
                    lost = previous_neighbors.difference(neighbors)
                    # print(previous_neighbors, neighbors)
                    # print(gained, lost)
                    # connections_lost and connections_gained will have all companies that even show up just once
                    for lost_company in lost:
                        connections_lost[company][lost_company] = timeframe
                    # connections_lost[company].update(lost)
                    for gained_company in gained:
                        connections_gained[company][gained_company] = timeframe
                    # connections_gained[company].update(gained)
                # The baseline is set to whenever the company first enters the timeframes
                if company not in previous_timeframe_connections:
                    baseline_timeframe_connections[company] = neighbors
                # if i == len(snapshots)-1:
                # This will only stop updating whenever the company leaves the timeframe
                final_timeframe_connections[company] =  neighbors
                previous_timeframe_connections[company] = neighbors
                degree = len(neighbors)
                average_degree += degree
                total_average_degree += degree
            snapshot_data[group] = average_degree/len(company_list)
        degree_data[timeframe] = snapshot_data
        total_average_degrees[timeframe] = total_average_degree/len(G.nodes)
    
    # Creates and plots impact data
    impact_data = {}
    fig = plt.figure()
    plot = fig.add_subplot(111)
    groups_to_remove = set()
    for group in filter:
        keep_group = True
        x_coords = []
        y_coords = []
        # Removes a group if it's not in every timeframe
        for timeframe in snapshots:
            if group not in degree_data[timeframe]:
                keep_group = False
                groups_to_remove.add(group)
                continue
            x_coords.append(timeframe)
            y_coords.append(degree_data[timeframe][group])
        if keep_group:
            baseline = y_coords[0]
            impact = max(baseline - min(y_coords), 0)
            total_impact = 0
            for coord in y_coords:
                total_impact += max(baseline - coord, 0)
            data = []
            data.append({x_coords[i]: y_coords[i] for i in range(len(x_coords))})
            data.append(impact)
            data.append(total_impact)
            impact_data[group] = data
            plot.plot(x_coords, y_coords, label=group)
    plot.plot(snapshots, list(total_average_degrees.values()), linewidth="5", markersize="6")

    # This keeps the impact data following the same criteria as the connections data
    for group in groups_to_remove:
        del filter[group]

    # Counts the makeup of connections over time, creating connections_data file. 
    connections_data = {}
    joined_connections = {}
    total_degree_difference = 0
    for group, company_list in filter.items():
        total_sum = 0
        total_reestablished_links = 0
        total_unestablished_links = 0
        total_lost_links = 0
        total_gained_links = 0
        for company in company_list:
            # Creates connections_change file by combining raw timestamps and company changes
            common_links = set(connections_lost[company].keys()).intersection(set(connections_gained[company].keys()))
            reestablished_links = set()
            unestablished_links = set()
            lost_links = set(connections_lost[company]).difference(common_links)
            gained_links = set(connections_gained[company]).difference(common_links)
            joined_connections[company] = {"lost":{}, "gained":{}, "unestablished":{}, "reestablished": {}}
            for company_link in common_links:
                if company_link in baseline_timeframe_connections[company]:
                    if company_link in final_timeframe_connections[company]:
                        # It was there at beginning and end, so it must've been lost first and then regained
                        reestablished_links.add(company_link)
                    else:
                        # It was just lost, even if it disappeared, reappeared, and then disappeared again
                        lost_links.add(company_link)
                else:
                    if company_link in final_timeframe_connections[company]:
                        # It was just gained, even if it appeared, disappeared, then appeared again
                        gained_links.add(company_link)
                    else:
                        # It was not there at beginning and end, so it must've been gained first and then lost
                        unestablished_links.add(company_link)
                # if connections_lost[company][company_link] < connections_gained[company][company_link]:
                #     reestablished_links += 1
                # elif connections_lost[company][company_link] > connections_gained[company][company_link]:
                #     unestablished_links += 1
                # else:
                #     print("MAJOR DATA FUCKUP!!", company, company_link)
            for link in lost_links:
                joined_connections[company]["lost"][link] = connections_lost[company][link]
            for link in gained_links:
                joined_connections[company]["gained"][link] = connections_gained[company][link]
            for link in unestablished_links:
                joined_connections[company]["unestablished"][link] = connections_lost[company][link]
            for link in reestablished_links:
                joined_connections[company]["reestablished"][link] = connections_gained[company][link]
            # reestablished_links = len(connections_lost[company].intersection(connections_gained[company]))
            total_reestablished_links += len(reestablished_links)
            total_unestablished_links += len(unestablished_links)
            total_lost_links += len(lost_links)
            total_gained_links += len(gained_links)
            total_sum += len(unestablished_links) + len(reestablished_links) + len(lost_links) + len(gained_links)
            # print(connections_lost[company], connections_gained[company], connections_lost[company].intersection(connections_gained[company]), company)
        if total_sum == 0:
            continue
        degree_difference = total_gained_links-total_lost_links
        total_degree_difference += degree_difference
        connections_data[group] = {"unestablished": total_unestablished_links/total_sum, "reestablished" : total_reestablished_links/total_sum, "lost" : total_lost_links/total_sum, "gained" : total_gained_links/total_sum, "degree_difference":degree_difference}
    with open(f"../data/{crisis}_companies_connections_change.json", "w") as f:
        json.dump(joined_connections, f, indent=4)
    with open(f"../data/{crisis}_{grouping}_connections_data.json", "w") as f:
        json.dump(connections_data, f, indent=4)
    with open(f"../data/{crisis}_{grouping}_impact_data.json", "w") as f:
        json.dump(impact_data, f, indent=4)

    print(total_degree_difference)
    # fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)           
    fig.show()
    if len(filter) < 10:
        fig.legend(loc='upper left')
    plt.savefig(f"../graphs/{crisis}_crisis_analysis_by_{grouping}.png")

def longitudinal_analysis(crisis, grouping):
    """
    Take the crisis impact data and fit some kind of equation to it or analyze the relationship between the filter and the impact data.
    """
    if crisis == "2008":
        snapshots = [17540, 17620, 17720, 17820, 18020, 18120, 18220, 18320, 18420, 18520, 18620, 18720, 18820, 18920, 19020, 19120, 19220, 19320, 19420, 19520]
        # snapshots = [17540, 17620]
    if crisis == "covid":
        snapshots = [21870, 21930, 21960, 22000, 22100, 22200, 22300, 22370]
        # snapshots = [21870, 21930]
    with open(f"../data/{crisis}_{grouping}_connections_data.json", "r") as f:
        connections_data = json.load(f)
    with open(f"../data/{crisis}_companies_connections_change.json", "r") as f:
        connections_timeframe = json.load(f)
    with open(f"../data/{crisis}_{grouping}_impact_data.json", "r") as f:
        impact_data = json.load(f)
    fig = plt.figure()
    # X-axis is absolute impact (deepest decreases), Y-axis is total impact (relative to beginning baseline)
    absolute_impacts = []
    total_impacts = []
    for company in connections_data:
        absolute_impacts.append(impact_data[company][1])
        total_impacts.append(impact_data[company][2])
        plt.scatter(impact_data[company][1], impact_data[company][2])
    plt.xlabel("Absolute impact")
    plt.ylabel("Total impact")
    plt.savefig(f"../graphs/{crisis}_{grouping}_absolute_total_impact.png")
    fig.clear()
    plt.hist(absolute_impacts)
    plt.savefig(f"../graphs/{crisis}_{grouping}_absolute_impact_histogram.png")
    fig.clear()
    plt.hist(total_impacts)
    plt.savefig(f"../graphs/{crisis}_{grouping}_total_impact_histogram.png")
    fig.clear()

    # TODO: MAYBE SPLIT THIS BY GROUPING?
    lost_histogram = {timeframe : 0 for timeframe in snapshots}
    gained_histogram = {timeframe : 0 for timeframe in snapshots}
    unestablished_histogram = {timeframe : 0 for timeframe in snapshots}
    reestablished_histogram = {timeframe : 0 for timeframe in snapshots}
    for connection_types in connections_timeframe.values():
        for type, companies in connection_types.items():
            for timeframe in companies.values():
                exec(type + "_histogram["+ str(timeframe) + "] += 1")
    print(lost_histogram)
    plt.plot(snapshots, lost_histogram.values(), label="Lost")
    plt.plot(snapshots, gained_histogram.values(), label="Gained")
    plt.plot(snapshots, unestablished_histogram.values(), label="Unestablished")
    plt.plot(snapshots, reestablished_histogram.values(), label="Reestablished")
    plt.legend(loc="upper left")
    plt.savefig(f"../graphs/{crisis}_connections_change_timeframe.png")

if __name__ == "__main__":
    crisis = sys.argv[1]
    grouping = sys.argv[2]
    # longitudinal_extraction(crisis, grouping)
    longitudinal_analysis(crisis, grouping)