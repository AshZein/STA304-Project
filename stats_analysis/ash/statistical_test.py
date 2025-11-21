from scipy.stats import f_oneway


def perform_anova_test(df):
    # Perform one-way ANOVA to test if mean fines differ by AREA_NAME
    groups = [g["set_fine_amount"] for _, g in df.groupby("AREA_L_CD")]
    f_stat, p = f_oneway(*groups)
    print(f"ANOVA F-statistic: {f_stat}, p-value: {p}")