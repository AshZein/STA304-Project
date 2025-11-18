import pandas as pd
import numpy as np
from utils import *

df = load_all_seasonal_data()

# GROUP BY SEASON
season_summary = df.groupby('season').agg(
    ticket_count=('set_fine_amount', 'count'),
    mean_fine=('set_fine_amount', 'mean'),
    median_fine=('set_fine_amount', 'median')
).reset_index()

print(season_summary)

# GROUP BY MONTH
df['date_of_infraction'] = pd.to_datetime(df['date_of_infraction'])
df['month'] = df['date_of_infraction'].dt.month
month_summary = df.groupby('month').agg(
    ticket_count=('set_fine_amount', 'count'),
    mean_fine=('set_fine_amount', 'mean'),
    median_fine=('set_fine_amount', 'median')
).reset_index()

print(month_summary)

print("most frequent infractions:\n", df['infraction_description'].value_counts().head(10))

print("conditional percentages:\n", pd.crosstab(df['season'], df['infraction_description'], normalize='index'))

counts = df.groupby(['season', 'infraction_description']).size()
top_each_season = counts.groupby(level=0).idxmax().reset_index(name='top_infraction')
top_each_season['count'] = counts.loc[top_each_season['top_infraction']].values
print(top_each_season)