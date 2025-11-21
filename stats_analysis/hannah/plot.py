import matplotlib.pyplot as plt
import numpy as np

def plot_boxplot(df, category_col, value_col, colors=None, title=None,
                 xlabel=None, ylabel=None, xlim=None):
    """
    Creates a vertical boxplot of value_col grouped by category_col,
    with median labels above each box and n-sizes below.
    """
    categories = sorted(df[category_col].dropna().unique())
    data = [df[df[category_col] == cat][value_col].dropna() for cat in categories]

    if colors is None:
        colors = ['#eee'] * len(categories)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor('#eee')

    bp = ax.boxplot(
        data,
        vert=True,
        labels=categories,
        patch_artist=True,
        medianprops=dict(color='red', linewidth=2),
        whiskerprops=dict(color='black', linewidth=2),
        capprops=dict(color='black', linewidth=2),
        boxprops=dict(edgecolor='black', linewidth=2)
    )

    # Color the boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor('black')
        patch.set_linewidth(2.5)

    # ---------------------------------------------------------
    # Add median labels
    # ---------------------------------------------------------
    medians = [med.get_ydata()[0] for med in bp['medians']]
    for i, median_val in enumerate(medians):
        ax.text(
            i + 1, median_val + (0.015 * median_val),  # position slightly above median line
            f"{median_val:.1f}",
            ha='center', va='bottom',
            fontsize=10
        )

    # ---------------------------------------------------------
    # Add sample size labels (n)
    # ---------------------------------------------------------
    for i, arr in enumerate(data):
        ax.text(
            i + 1,                     # x-position under the box
            -3,  # push below the lowest box area
            f"n={len(arr)}",
            ha='center', va='top',
            fontsize=10, color='black'
        )

    # Labels & Title
    if xlabel: ax.set_xlabel(xlabel, fontsize=14)
    if ylabel: ax.set_ylabel(ylabel, fontsize=14)
    if title: ax.set_title(title, fontsize=16)

    ax.tick_params(labelsize=12)

    if xlim:
        plt.ylim(-5, xlim)

    plt.grid(True, color='white', alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_bar(categories, values, title=None, xlabel=None, ylabel=None, show_mean_sd=True):
    """
    Barplot for aggregated data.

    categories : list or pandas Series (x-axis)
    values     : list or pandas Series (heights)
    """

    # Convert to numpy
    categories = np.array(categories)
    values = np.array(values)

    # Compute mean and SD over the aggregated values
    mean_val = values.mean()
    std_val = values.std()

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor('#eee')

    # --- Shaded mean ± SD region (optional) ---
    if show_mean_sd:
        ax.axhspan(mean_val - std_val, mean_val + std_val,
                   color='gray', alpha=0.25, zorder=0)
        ax.axhline(mean_val, color='black', linestyle='--', linewidth=2, zorder=1)

    # --- Bars (matching your boxplot aesthetics) ---
    bars = ax.bar(
        categories,
        values,
        width=1.0,
        edgecolor='white',
        linewidth=2.0,
        color='#F87C63',
        alpha=0.9
    )

    # --- Label each bar with its numeric value ---
    for i, v in enumerate(values):
        ax.text(
            i+1, v + 0.02 * max(values),  # month needs i + 1, v + 0.02 * max(values) for some reason
            f"{v:.0f}",  # integer count
            ha='center', va='bottom',
            fontsize=10
        )

    # --- Labels ---
    if xlabel: ax.set_xlabel(xlabel, fontsize=14)
    if ylabel: ax.set_ylabel(ylabel, fontsize=14)
    if title: ax.set_title(title, fontsize=16)

    ax.tick_params(labelsize=12)
    plt.grid(True, color='white', alpha=0.15)
    plt.tight_layout()
    plt.show()
