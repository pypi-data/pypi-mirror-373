from lukhed_basic_utils import mathCommon as mC


def add_scatter_points_to_chart(ax, x, y, dot_size="auto", dot_color="auto", marker="auto", best_fit_line=False):
    """
    :param ax:
    :param x:
    :param y:
    :param dot_size: int() or array(), If int, all dots will be applied the size. If array, it must match the array
                     given for the plot (i.e. 1 to 1 in size to dot)
    :param dot_color:
    :param marker: str(), options: ., o, s, ^, v, +, x
                   https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
    :param best_fit_line:
    :return:
    """

    np = mC.get_np()
    if dot_color == "auto":
        dot_color = None
    if marker == "auto":
        marker = None

    if dot_size != "auto":
        scatter = ax.scatter(x, y, zorder=2, s=dot_size, c=dot_color, marker=marker)
    else:
        scatter = ax.scatter(x, y, zorder=2, c=dot_color, marker=marker)


    if best_fit_line:
        data = np.polyfit(x, y, 1)
        m = data[0]
        b = data[1]
        x_point = (y[0] - b) / m
        ax.axline((x_point, y[0]), slope=m)

    return scatter


def update_scatter_formatting(scatter, dot_size="auto", dot_color="auto"):
    """
    :param scatter: scatter object, as returned by the main scatter chart creations.
    :param dot_size: list(), must be list same length as there are dots
    :param dot_color: str() or list(). Str() of color will make all dots same color. Or customize each with array
    :return:
    """
    if dot_color != "auto":
        scatter.set_sizes(dot_size)
    if dot_color != "auto":
        scatter.set_color(dot_color)

    return scatter
