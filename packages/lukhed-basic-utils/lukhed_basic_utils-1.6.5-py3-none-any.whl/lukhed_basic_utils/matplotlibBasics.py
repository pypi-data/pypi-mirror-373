from matplotlib.offsetbox import OffsetImage
from matplotlib import pyplot as plt


def get_plt():
    """
    This function is used to get the plt object from the module. It is used to avoid circular imports.
    :return:
    """
    return plt


def create_sub_plots():
    fig, ax = plt.subplots(figsize=(16, 9))
    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": None,
        "x": None,
        "y": None,
        "plt": plt
    }


def clear_plot(ax):
    ax.cla()


def recreate_figure_after_close(fig):
    """
    This function can be used in classes that allow opening/closing figures. After a user closes an image, the GUI
    is destroyed (FigureManager). This function adds back a FigureManager to a figure so it can be opened again.

    https://stackoverflow.com/questions/31729948/matplotlib-how-to-show-a-figure-that-has-been-closed

    :param fig:
    :return:
    """
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)


def save_fig(fig, full_path_location, pad_inches=.2, bbox_inches='tight'):
    fig.savefig(full_path_location, bbox_inches=bbox_inches, pad_inches=pad_inches)


def get_image(path, plt, zoom):
    return OffsetImage(plt.imread(path), zoom=zoom)
