from matplotlib.offsetbox import AnnotationBbox
from lukhed_basic_utils import matplotlibBasics, matplotlibFormatting, mathCommon as mC

def bar_chart_with_images_as_labels(x_list, y_list, image_list, image_zoom="auto", show_image=False, save_image=None,
                                    y_range_tuple=None, bar_colors=None, bar_width_multiplier=None, twitter_resize=True,
                                    image_y_offset=0, image_x_offset=0, hide_x_axis=False, hide_y_axis=False,
                                    x_margin="auto", y_margin="auto", grid=False):
    np = mC.get_np()
    plt = matplotlibBasics.get_plt()
    fig, ax = plt.subplots(figsize=(16, 9))     # returns figure and axes (axes.Axes)
    # https://matplotlib.org/stable/api/axes_api.html#matplotlib.axes.Axes
    # https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure


    if image_zoom == "auto":
        if len(x_list) <= 5:
            image_zoom = .3
        else:
            image_zoom = 1

    # Add images above y data point
    for x0, y0, path in zip(np.arange(0, len(x_list)), y_list, image_list):
        ab = AnnotationBbox(matplotlibBasics.get_image(path, plt, image_zoom), (x0 + image_x_offset, y0 + image_y_offset), frameon=False)
        ax.add_artist(ab)


    # Create the bar chart
    ax.bar(x_list, y_list)

    # Format the bar chart
    ax = matplotlibFormatting.bar_chart_formatting(ax, y_range_tuple=y_range_tuple, bar_colors=bar_colors,
                              bar_width_multiplier=bar_width_multiplier, hide_y_axis=hide_y_axis,
                              hide_x_axis=hide_x_axis, x_margin=x_margin, y_margin=y_margin, grid=grid)

    if twitter_resize:
        ax = matplotlibFormatting.resize_plot_for_twitter(ax)


    if show_image:
        fig.show()
    if save_image is not None:
        fig.savefig(save_image)

    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": save_image,
        "x": x_list,
        "y": y_list
    }

    