from matplotlib.scale import LogScale
import pandas as pd
import numpy as np
from utils import *
import sys
sys.path.append('C:/Users/jilli/OneDrive/Documents/UofT/Courses/sta304/group_proj/STA304-Project-1/stats_analysis/ash')
from graphics import *
import matplotlib.pyplot as plt
import seaborn as sns

df = load_all_seasonal_data()
df['tag_number_masked'] = df['tag_number_masked'].astype(str)
df['date_of_infraction'] = pd.to_datetime(df['date_of_infraction'])
df['infraction_code'] = df['infraction_code'].astype(int)
df['infraction_description'] = df['infraction_description'].astype(str)
df['location1'] = df['location1'].astype(str)
df['season'] = df['season'].astype(str)

# print(df.info(), df.describe())

# GROUP BY SEASON
season_summary = df.groupby('season').agg(
    ticket_count=('set_fine_amount', 'count'),
    mean_fine=('set_fine_amount', 'mean'),
    median_fine=('set_fine_amount', 'median')
).reset_index()
print(season_summary)

# GROUP BY MONTH
month_summary = df.groupby('month').agg(
    ticket_count=('set_fine_amount', 'count'),
    mean_fine=('set_fine_amount', 'mean'),
    median_fine=('set_fine_amount', 'median')
).reset_index()

print(month_summary)

# GROUP BY HOUR
hour_summary = df.groupby('hour').agg(
    ticket_count=('set_fine_amount', 'count'),
    mean_fine=('set_fine_amount', 'mean'),
    median_fine=('set_fine_amount', 'median')
).reset_index()

print(hour_summary)


# print("\n most frequent infractions:\n", df['infraction_description'].value_counts().head(10))

# print("conditional percentages:/n", pd.crosstab(df['season'], df['infraction_description'], normalize='index'))

# print("\n top infraction type per season:\n")
# counts = df.groupby(['season', 'infraction_description']).size()
# top_each_season = counts.groupby(level=0).idxmax().reset_index(name='top_infraction')
# top_each_season['count'] = counts.loc[top_each_season['top_infraction']].values
# print(top_each_season)

# print("\n top infraction type per month:\n")
# counts = df.groupby(['month', 'infraction_description']).size()
# top_each_season = counts.groupby(level=0).idxmax().reset_index(name='top_infraction')
# top_each_season['count'] = counts.loc[top_each_season['top_infraction']].values
# print(top_each_season)

# print("\n top infraction type per hour:\n")
# counts = df.groupby(['hour', 'infraction_description']).size()
# top_each_season = counts.groupby(level=0).idxmax().reset_index(name='top_infraction')
# top_each_season['count'] = counts.loc[top_each_season['top_infraction']].values
# print(top_each_season)

# df['year'] = df['date_of_infraction'].dt.year
# print(df['year'].unique)
# season_by_year_pct = pd.crosstab(
#     df['year'],
#     df['season'],
#     normalize='index'
# ) * 100
# print(season_by_year_pct)
# ax = season_by_year_pct.plot(
#     kind='bar',
#     stacked=True,
#     figsize=(12,8),
#     colormap='tab20c'
# )

# plt.ylabel("Conditional Percentage of Tickets (%)")
# plt.title("Seasonal Distribution of Tickets by Year")
# plt.legend(title='Season', loc='right')
# plt.xticks(rotation=0)

# # Add percentages on the bars
# for p in ax.patches:
#     width, height = p.get_width(), p.get_height()
#     if height > 0:  # avoid labeling 0 height bars
#         x, y = p.get_xy()
#         ax.text(
#             x + width/2,        # center x
#             y + height/2,       # center y
#             f'{height:.1f}%',   # display height as percentage
#             ha='center',
#             va='center',
#             fontsize=10,
#             color='black'
#         )

# plt.show()

# FIGURES

from plot import *

# plot_boxplot(df, category_col='season', value_col='set_fine_amount', ylabel='Fine Amount ($)', xlabel='Season', 
#              title='Fine Distribution by Season', xlim=100)
# plot_boxplot(df, category_col='month', value_col='set_fine_amount', ylabel='Fine Amount ($)', xlabel='Month', 
#              title='Fine Distribution by Month', xlim=100)
# plot_boxplot(df, category_col='hour', value_col='set_fine_amount', ylabel='Fine Amount ($)', xlabel='Hour of Day', 
#              title='Fine Distribution by Hour', xlim=100)

# plot_bar(
#     categories=season_summary['season'],
#     values=season_summary['ticket_count'],
#     title='Total Tickets per Season',
#     xlabel='Season',
#     ylabel='Ticket Count',
#     show_mean_sd=False
# )
plot_bar(
    categories=month_summary['month'],
    values=month_summary['ticket_count'],
    title='Total Tickets per Month',
    xlabel='Month',
    ylabel='Ticket Count',
    show_mean_sd=False
)
# plot_bar(
#     categories=hour_summary['hour'],
#     values=hour_summary['ticket_count'],
#     title='Total Tickets per Hour',
#     xlabel='Hour',
#     ylabel='Ticket Count',
#     show_mean_sd=False
# )
