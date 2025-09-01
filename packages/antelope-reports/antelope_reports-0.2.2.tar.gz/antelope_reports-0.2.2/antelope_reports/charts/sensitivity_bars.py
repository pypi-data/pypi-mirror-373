import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import get_cmap


def sensitivity_bars(df, baseline='Baseline', lo='Low_5', hi='High_95', colors=None, cmap='tab10'):
    """
    Requires a dataframe with columns "Case", "Variant", "Quantity", "Indicator", and baseline, lo, and hi columns.

    Creates a grid where each row is a quantity, each column is a case, and each facet is a barchart where individual
    bars are variants.  Draws a bar of height baseline and errorbars spanning from lo to hi.

    :param df:
    :param baseline: 'Baseline' Column containing baseline data
    :param lo: 'Low_5' Column containing low-sens data
    :param hi: 'High_95' Column containing high-sens data
    :param colors: None a list of colors corresponding to variants
    :param cmap: 'tab10' if no colors are specified, the colormap from which to draw colors
    :return:
    """
    """
    :param df: 
    :return: 
    """
    # Get unique cases and quantities
    cases = df['Case'].unique()
    quantities = df['Quantity'].unique()
    variants = df['Variant'].unique()

    # Create subplot grid
    fig, axes = plt.subplots(
        len(quantities), len(cases), figsize=(2 * len(cases), 1.6 * len(quantities)), sharey=False, sharex=True
    )

    # Ensure axes is a 2D array for consistent indexing
    if len(quantities) == 1:
        axes = [axes]
    if len(cases) == 1:
        axes = np.array(axes).reshape(-1, 1)

    # Define colors for variants
    n = len(variants)
    if colors is None:
        colors = get_cmap(cmap, n)(np.arange(len(variants)))

    # store ylims by quantity
    row_y_limits = []
    # Iterate through cases and quantities to plot
    for i, quantity in enumerate(quantities):
        y_min, y_max = float('inf'), float('-inf')
        for j, case in enumerate(cases):
            ax = axes[i][j]

            # Filter data for the current case and quantity
            sub_df = df[(df['Case'] == case) & (df['Quantity'] == quantity)]

            # X positions for the bars
            x_positions = np.arange(len(variants))

            # Plot bars with error bars
            ax.bar(
                x_positions,
                sub_df[baseline],
                yerr=[
                    sub_df[baseline] - sub_df[lo],
                    sub_df[hi] - sub_df[baseline]
                ],
                width=0.66,
                capsize=4,
                color=colors[:len(sub_df)],
                edgecolor='none',
                tick_label=sub_df['Variant']
            )

            # Set subplot title and labels
            if i == 0:
                ax.set_title(f"Case: {case}")
            if j == 0:
                ax.set_ylabel(sub_df.iloc[0]['Indicator'])

            ax.set_xticks(x_positions)
            ax.set_yticks([])
            ax.set_xlim([x_positions[0] - 0.7, x_positions[-1] + 0.7])
            ax.set_xticklabels(sub_df['Variant'], rotation=45, ha='right')
            # Update y-axis limits
            current_min, current_max = ax.get_ylim()
            y_min = min(y_min, current_min)
            y_max = max(y_max, current_max)

        # Store the calculated limits for the row
        row_y_limits.append((y_min, y_max))
        for j in range(len(cases)):
            axes[i][j].set_ylim((y_min, y_max))

    return fig
