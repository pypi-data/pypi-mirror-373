from matplotlib.offsetbox import AnnotationBbox
from lukhed_basic_utils import matplotlibBasics, matplotlibFormatting


def line_chart_with_images_as_labels(x_list, y_list, image_list, image_zoom="auto", image_y_offset=0, image_x_offset=0,
                                     save_image=None, show_image=False, color="blue"):
    plt = matplotlibBasics.get_plt()
    fig, ax = plt.subplots(figsize=(16, 9))  # returns figure and axes (axes.Axes)
    # https://matplotlib.org/stable/api/axes_api.html#matplotlib.axes.Axes
    # https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure

    image_zoom = matplotlibFormatting.parse_image_zoom_parameter(image_zoom, x_list)

    # Add images above y data point
    for x0, y0, path in zip(x_list, y_list, image_list):
        ab = AnnotationBbox(
            matplotlibBasics.get_image(path, plt, image_zoom),
            (x0 + image_x_offset, y0 + image_y_offset), frameon=False)
        ax.add_artist(ab)

    add_line_to_chart(ax, y_list, x_list, color=color)

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


def add_line_to_chart(ax, y_list, x_list=None, df=None, color="blue", label=None, linewidth=None):
    if x_list is None:
        ax.plot(y_list, color=color, label=label, linewidth=linewidth)
    elif x_list is not None:
        ax.plot(x_list, y_list, color=color, label=label, linewidth=linewidth)
    else:
        ax.plot(df, color=color, label=label, linewidth=linewidth)


def add_vertical_line(ax, x, color=None, linestyle=None, linewidth=None):
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    ax.axvline(x, color=color, linestyle=linestyle, linewidth=linewidth)


def add_horizontal_line(ax, y, color=None, linestyle=None, linewidth=None):
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    ax.axhline(y, color=color, linestyle=linestyle, linewidth=linewidth)


def create_line_chart_from_lists(x_list, y_list, save_image=None, show_image=False, color="blue",
                                 label=None, linewidth=None):
    plt = matplotlibFormatting.get_plt()
    fig, ax = plt.subplots(figsize=(16, 9))  # returns figure and axes (axes.Axes)
    # https://matplotlib.org/stable/api/axes_api.html#matplotlib.axes.Axes
    # https://matplotlib.org/stable/api/figure_api.html#matplotlib.figure.Figure


    if label is None:
        add_line_to_chart(ax, y_list, x_list, color=color, linewidth=linewidth)
    else:
        add_line_to_chart(ax, y_list, x_list, color=color, label=label, linewidth=linewidth)

    if show_image:
        fig.show()
    if save_image is not None:
        fig.savefig(save_image)

    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": save_image,
        "x": x_list,
        "y": y_list,
        "plt": plt
    }


def create_line_chart_from_data_frame(df):
    """
    This function can be used to quickly create a line chart from a dataframe
    :param df: pandas data frame
    :param color: str(), color or hext code for line
    :return: dict(), with plot information ready.
    """

    plt = matplotlibFormatting.get_plt()
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.plot(df)
    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": None,
        "df": df
    }

