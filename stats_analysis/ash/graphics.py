import matplotlib.pyplot as plt
import seaborn as sns

def create_box_plot(data, x_col, y_col, title, output_path):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=x_col, y=y_col, data=data)
    plt.title(title)
    plt.savefig(output_path)
    plt.close()
    
def create_histogram(data, col, bins, title, output_path):
    #col is the one we want to plot, like 'set_fine_amount'
    plt.figure(figsize=(10, 6))
    plt.hist(data[col], bins=bins, edgecolor='black')
    plt.title(title)
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.savefig(output_path)
    plt.close()
    
def create_summary_statistics(data, col):
    summary = data[col].describe()
    plt.figure(figsize=(8, 4))
    plt.table(cellText=[summary.values], colLabels=summary.index, loc='center', cellLoc='center')
    plt.axis('off')
    plt.title(f'Summary Statistics for {col}')
    plt.savefig(f'summary_stats_{col}.png')
    plt.close()
    return summary