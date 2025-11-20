import scipy.stats as stats
import pandas as pd
import statsmodels.formula.api as smf
from utils import *

# average fines only vary by hour
# total tickets vary by season, month, hour

df = load_all_seasonal_data()

# # chi-square
# # to test if ticket volumes differ by season/month/hour
# contingency = pd.crosstab(df['season'], df['month'])  # or season x hour
# stats.chi2_contingency(contingency)
# # print(contingency)

# # regression
# # to test if hour can predict fine amount
# model = smf.ols("set_fine_amount ~ C(hour)", data=df).fit()
# # print(model.summary())
# model_season = smf.ols("set_fine_amount ~ C(season)", data=df).fit()
# # print(model_season.summary())
# model_month = smf.ols("set_fine_amount ~ C(month)", data=df).fit()
# # print(model_month.summary())

# model_full = smf.ols(
#     "set_fine_amount ~ C(season) + C(month) + C(hour)",
#     data=df
# ).fit()
# # print(model_full.summary())

# # anova
# # to test whether fine amounts differ by season/month/hour
# anova_season = stats.f_oneway(
#     *[group['set_fine_amount'].dropna() 
#       for name, group in df.groupby('season')]
# )
# print("ANOVA by Season")
# print(anova_season)

# anova_month = stats.f_oneway(
#     *[group['set_fine_amount'].dropna()
#       for name, group in df.groupby('month')]
# )

# print("ANOVA by Month")
# print(anova_month)

# anova_hour = stats.f_oneway(
#     *[group['set_fine_amount'].dropna()
#       for name, group in df.groupby('hour')]
# )

# print("ANOVA by Hour")
# print(anova_hour)


# ticket counts
import statsmodels.api as sm

# Aggregate by day (or hour)
df_counts = df.groupby(['date_of_infraction', 'season', 'month', 'hour']).size().reset_index(name='ticket_count')

# Poisson regression
model = smf.glm(formula='ticket_count ~ C(season) + C(month) + C(hour)',
                data=df_counts,
                family=sm.families.Poisson()).fit()

print(model.summary())
