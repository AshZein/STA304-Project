import pandas as pd
from pathlib import Path
import glob, os, sys
from utils import *

# Load data
df = load_all_seasonal_data()
print(df, df.columns)

# -------------------------------------------------------------
# CLEAN / NORMALIZE TIME FIELD
# -------------------------------------------------------------
# time_of_infraction is in float form like 1.0 → convert to int hour 1
df["hour"] = df["time_of_infraction"].astype(str)[:2]

# -------------------------------------------------------------
# MOST FREQUENT INFRACTION PER HOUR (across all seasons/years)
# -------------------------------------------------------------
most_freq_per_hour = (
    df.groupby(["hour", "infraction_code", "infraction_description"])
      .size()
      .reset_index(name="count")
)

# For each hour, keep only the rows with the max count
most_freq_per_hour = (
    most_freq_per_hour
    .sort_values(["hour", "count"], ascending=[True, False])
    .groupby("hour")
    .head(1)
)

print("/n=== Most Frequent Infraction Per Hour ===")
print(most_freq_per_hour)

# -------------------------------------------------------------
# MOST FREQUENT INFRACTION PER SEASON
# -------------------------------------------------------------
most_freq_per_season = (
    df.groupby(["season", "infraction_code", "infraction_description"])
      .size()
      .reset_index(name="count")
)

most_freq_per_season = (
    most_freq_per_season
    .sort_values(["season", "count"], ascending=[True, False])
    .groupby("season")
    .head(1)
)

print("/n=== Most Frequent Infraction Per Season ===")
print(most_freq_per_season)
