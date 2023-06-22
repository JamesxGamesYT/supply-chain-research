import pandas as pd
import sys
date = pd.to_datetime(int(sys.argv[1]), origin='1960-01-01', unit='D')
print(f"Date: {date}")