import pandas as pd
import glob, os, sys

def combine_dfs(path):
    df = None
    for f in glob.glob(path):
        imp = pd.read_csv(f)
        if not df:
            df = imp
        else:
            pd.merge(df, imp, how='inner')
    
    return df

# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
DATA_DIR = "C:/Users/jilli/STA304/data/seasons"
SEASONS = ["winter", "spring", "summer", "fall"]
YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
# File pattern: parking_data_{year}_{season}.csv
# -------------------------------------------------------------

def load_all_seasonal_data():
    """Load all CSVs for all years + seasons into one DataFrame."""
    print("Loading seasonal data...")
    frames = []
    for yr in YEARS:
        for season in SEASONS:
            path = os.path.join(DATA_DIR, season)
            file_path = path + f"/parking_data_{yr}_{season}.csv"
            df = pd.read_csv(file_path)
            df["season"] = season
            df["year"] = yr
            frames.append(df)
    df_final = pd.concat(frames, ignore_index=True)
    df_final = df_final.dropna()
    df_final = df_final.drop_duplicates()
    print("Loaded data into dataframe.")
    return df_final