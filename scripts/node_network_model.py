import pandas as pd
import networkx as nx

def company_network_analysis():



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
    fit_model(timeframes)