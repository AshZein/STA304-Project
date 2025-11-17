import pandas as pd
import glob

def combine_dfs(path):
    df = None
    for f in glob.glob(path):
        imp = pd.read_csv(f)
        if not df:
            df = imp
        else:
            pd.merge(df, imp, how='inner')
    
    return df