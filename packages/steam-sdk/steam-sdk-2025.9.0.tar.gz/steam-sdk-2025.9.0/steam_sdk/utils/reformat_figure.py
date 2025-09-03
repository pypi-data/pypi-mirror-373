import matplotlib.pyplot as plt


def reformat_figure(fig=None, figsize=None, label_font=None, title_font=None, legend_font=None, tick_font=None, grid=True, box=True, subplots_adjust_params=None):
    """
    Reformat an existing figure.

    Parameters:
        - fig (matplotlib.figure.Figure): The existing figure object.
        - figsize (tuple, optional): The new figure size in inches (width, height). If not provided, the figure size remains unchanged.
        - label_font (dict, optional): Font properties for x/y labels.
        - title_font (dict, optional): Font properties for the figure title.
        - legend_font (dict, optional): Font properties for the legend entries.
        - tick_font (dict, optional): Font properties for x/y ticks.
        - grid (bool, optional): Whether to add grid lines to the plot.
        - box (bool, optional): Whether to add a box around the plot.
        - subplots_adjust_params (dict, optional): Parameters for adjusting subplots using `plt.subplots_adjust()`.
    """

    if not fig:
        fig = plt.gcf()

    # Define the default formatting options
    if not figsize:
        figsize = (20/2.54, 15/2.54)  # 20 cm by 15 cm
    if not label_font:
        label_font = {'fontname': 'DejaVu Sans', 'size': 16}
    if not title_font:
        title_font = {'fontname': 'DejaVu Sans', 'size': 16}
    if not legend_font:
        legend_font = {'fontname': 'DejaVu Sans', 'size': 14}
    if not tick_font:
        tick_font = {'fontname': 'DejaVu Sans', 'size': 12}
    if not grid:
        grid = True
    if not box:
        box = True
    if not subplots_adjust_params:
        subplots_adjust_params = {'left': 0.1, 'right': 0.9, 'bottom': 0.1, 'top': 0.9}


    # Set the figure size
    fig.set_size_inches(figsize)

    # Assign font to x/y labels
    for ax in fig.axes:
        ax.set_xlabel(ax.get_xlabel(), **label_font)
        ax.set_ylabel(ax.get_ylabel(), **label_font)

    # Assign font to title
    if fig._suptitle:
        fig.suptitle(fig._suptitle.get_text(), **title_font)

    # Assign font to legend entries
    for ax in fig.axes:
        legend = ax.legend()
        if legend:
            legend_texts = legend.get_texts()
            if legend_texts:
                plt.setp(legend_texts, **legend_font)

    # Assign font to ticks
    for ax in fig.axes:
        # This bit of code is needed to avoid inconsistencies between ticks and ticks labels
        ax.set_xticks([])  # clears manual ticks
        ax.set_yticks([])  # clears manual ticks
        ax.xaxis.set_major_locator(plt.AutoLocator())  # restore automatic behavior
        ax.yaxis.set_major_locator(plt.AutoLocator())  # restore automatic behavior
        ax.xaxis.set_major_formatter(plt.ScalarFormatter())  # reset formatter to default
        ax.yaxis.set_major_formatter(plt.ScalarFormatter())  # reset formatter to default
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()
        x_ticks = ax.get_xticks()
        y_ticks = ax.get_yticks()
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)
        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        # Change font of the tick labels
        ax.set_xticklabels(ax.get_xticklabels(), **tick_font)
        ax.set_yticklabels(ax.get_yticklabels(), **tick_font)
        # Restore once again the automatic tick behavior (needed in case one manually zooms in the figure afterwards)
        ax.set_xticks([])  # clears manual ticks
        ax.set_yticks([])  # clears manual ticks
        ax.xaxis.set_major_locator(plt.AutoLocator())  # restore automatic behavior
        ax.yaxis.set_major_locator(plt.AutoLocator())  # restore automatic behavior
        ax.xaxis.set_major_formatter(plt.ScalarFormatter())  # reset formatter to default
        ax.yaxis.set_major_formatter(plt.ScalarFormatter())  # reset formatter to default

    # Add grid
    if grid:
        for ax in fig.axes:
            ax.grid(True)

    # Add box
    if box:
        for ax in fig.axes:
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)

    # Adjust subplots
    # plt.subplots_adjust(**subplots_adjust_params)
    fig.tight_layout()
