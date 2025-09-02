from matplotlib.offsetbox import AnnotationBbox
import matplotlib.dates as mdates
from matplotlib import ticker
from lukhed_basic_utils import matplotlibBasics, mathCommon as mC


def resize_plot_for_twitter(ax):
    ratio = 0.563
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * ratio)
    return ax


def move_legend_outside_plot(plt, location='upper left'):
    """

    :param location:        str(), upper left,
    :param plt:             plot module
    :return:
    """

    plt.legend(bbox_to_anchor=(1.02, 1), loc=location, borderaxespad=0)


def add_title_to_plot(fig, title_string, title_size="auto", color="black", padding=None):
    if title_size != "auto":
        fig.suptitle(title_string, fontsize=title_size, color=color)
    else:
        fig.suptitle(title_string, color=color)

    return fig


def add_title_to_subplot(ax, title_string, title_size="auto", color="black", padding=None):
    if title_size != "auto":
        ax.set_title(title_string, fontsize=title_size, color=color, pad=padding)
    else:
        ax.set_title(title_string, color=color, pad=padding)

    return ax


def add_title_to_axis(ax, title_string, x_or_y, title_size="auto", color="black", padding=None):
    x_or_y = x_or_y.lower()

    if x_or_y == "x":
        if title_size != "auto":
            ax.set_xlabel(title_string, fontsize=title_size, color=color, labelpad=padding)
        else:
            ax.set_xlabel(title_string, color=color, labelpad=padding)
    else:
        if title_size != "auto":
            ax.set_ylabel(title_string, fontsize=title_size, color=color, labelpad=padding)
        else:
            ax.set_ylabel(title_string, color=color, labelpad=padding)

    return ax


def add_legend_to_chart(ax, label_list):
    """
    Use "generate_and_show_legend" if you already have labels set up upon initial plot.

    This method is generally discouraged because the label list are assigned to plots after they are created in
    the order they are created. So you must know the order of the plots.

    It is generally better to set labels for the series as they are created
    :param ax:
    :param label_list:      list(), list of strings to serve as labels for the legend
    :return:
    """
    ax.legend(label_list)


def generate_and_show_legend(fig):
    """
    Use this function if you already set up labels for the plots. If you have no labels and want to add them
    manually, use add_legend_to_chart
    :param fig:
    :return:
    """

    fig.legend()


def basic_formatting(ax, hide_y_axis=False, hide_x_axis=False, x_margin="auto", y_margin="auto", grid=False,
                     y_range_tuple=None, x_range_tuple=None, y_step_size="auto", x_step_size="auto",
                     chart_area_color="white", x_label_size=None, x_label_color=None, y_label_size=None,
                     y_label_color=None, x_tick_color=None, y_tick_color=None):
    np = mC.get_np()
    if hide_x_axis:
        ax.axes.xaxis.set_visible(False)
    if hide_y_axis:
        ax.axes.yaxis.set_visible(False)
    if x_margin != "auto":
        ax.margins(x=x_margin)
    if y_margin != "auto":
        ax.margins(y=y_margin)
    if grid:
        ax.grid()
    if y_range_tuple is not None:
        ax.set_ylim(y_range_tuple)
    if x_range_tuple is not None:
        ax.set_xlim(x_range_tuple)
    if y_step_size != "auto":
        start, end = ax.get_ylim()
        ax.yaxis.set_ticks(np.arange(start, end, y_step_size))
    if x_step_size != "auto":
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(start, end, x_step_size))
    if chart_area_color != "white":
        ax.set_facecolor(chart_area_color)
    if x_label_size is not None:
        ax.tick_params("x", labelsize=x_label_size)
    if y_label_size is not None:
        ax.tick_params("y", labelsize=y_label_size)
    if x_label_color is not None:
        ax.tick_params("x", labelcolor=x_label_color)
    if y_label_color is not None:
        ax.tick_params("y", labelcolor=y_label_color)
    if x_tick_color is not None:
        ax.tick_params("x", color=x_tick_color)
    if y_tick_color is not None:
        ax.tick_params("y", color=y_tick_color)


def basic_formatting_fig(fig, background_color="white"):
    if background_color != "white":
        fig.patch.set_facecolor(background_color)


def set_detailed_ticks(ax, axis, start, end, step, tick_type="major"):
    np = mC.get_np()
    ticks = np.arange(start, end, step)
    if axis == "x":
        if tick_type == "major":
            ax.set_xticks(ticks)
        else:
            ax.set_xticks(ticks, minor=True)
    else:
        if tick_type == "major":
            ax.set_yticks(ticks)
        else:
            ax.set_yticks(ticks, minor=True)


def parse_image_zoom_parameter(image_zoom, x_list):
    if image_zoom == "auto":
        if len(x_list) <= 5:
            image_zoom = .3
        else:
            image_zoom = 1

    return image_zoom


def add_images_to_chart(ax, x_list, y_list, image_list, image_zoom=1, image_x_offset=0, image_y_offset=0):
    # Add images above y data point
    for x0, y0, path in zip(x_list, y_list, image_list):
        ab = AnnotationBbox(
            matplotlibBasics.get_image(path, matplotlibBasics.get_plt(), image_zoom),
            (x0 + image_x_offset, y0 + image_y_offset), frameon=False)
        ax.add_artist(ab)


def add_annotation(ax, text, point_tuple, color="black", fontsize=None, fontstyle=None):
    ax.annotate(text, point_tuple, color=color, fontsize=fontsize, fontstyle=None)


def toggle_legend(ax):
    ax.legend()


def auto_format_dates(fig, x_or_y="x"):
    """
    This function auto rotates the dates to fit on the plot (if too many major points are present, you need
    to use dates_major_spacing to change the spacing of labels
    :param fig:
    :param x_or_y:
    :return:
    """
    if x_or_y == "x":
        fig.autofmt_xdate()
    else:
        fig.autofmt_ydate()


def adjust_axis_major_ticks_dates(ax, interval="month", x_or_y="x"):
    """
    Use this
    :param ax:
    :param interval:        str(), day, week, month, year, hour, minute
    :param x_or_y:
    :return:
    """

    if interval == "minute":
        use_locator = mdates.MinuteLocator()
    elif interval == "hour":
        use_locator = mdates.HourLocator()
    elif interval == "day":
        use_locator = mdates.DayLocator()
    elif interval == "week":
        use_locator = mdates.WeekdayLocator()
    elif interval == "month":
        use_locator = mdates.MonthLocator()
    elif interval == "year":
        use_locator = mdates.YearLocator()
    else:
        use_locator = mdates.DayLocator()

    if x_or_y == "x":
        ax.xaxis.set_major_locator(use_locator)
    else:
        ax.yaxis.set_major_locator(use_locator)


def adjust_axis_major_ticks_segment(ax, number_of_segments, x_or_y="x"):
    if x_or_y == "x":
        ax.xaxis.set_major_locator(ticker.MultipleLocator(number_of_segments))
    else:
        ax.yaxis.set_major_locator(ticker.MultipleLocator(number_of_segments))


def add_dollar_symbols_to_axis(ax, x_or_y):
    tick_format = '${x:1.2f}'

    if x_or_y == "y":
        ax.yaxis.set_major_formatter(tick_format)
    else:
        ax.xaxis.set_major_formatter(tick_format)


def add_percent_symbols_to_axis(ax, x_or_y):
    if x_or_y == "y":
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    else:
        ax.xaxis.set_major_formatter(ticker.PercentFormatter())


def specify_axis_labels(ax, label_list, x_or_y):
    """
    Pass the exact amount of labels as points on the axis with the string you want for each.
    :param ax:
    :param label_list:
    :param x_or_y:
    :return:
    """

    if x_or_y == "y":
        ax.yaxis.set_major_formatter(ticker.FixedFormatter(label_list))
    else:
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(label_list))


def adjust_margins(ax, x_margin="auto", y_margin="auto"):
    if x_margin != "auto":
        ax.margins(x=x_margin)
    if y_margin != "auto":
        ax.margins(y=y_margin)

    return ax


def bar_chart_formatting(ax, y_range_tuple=None, bar_colors=None, bar_width_multiplier=None, hide_y_axis=False,
                         hide_x_axis=False, x_margin="auto", y_margin="auto", grid=False):
    if y_range_tuple is not None:
        ax.set_ylim(y_range_tuple)
    if bar_colors is not None:
        counter = 0
        for bar in ax.axes.containers[0]:
            bar.set_color(bar_colors[counter])
            counter = counter + 1
    if bar_width_multiplier is not None:
        counter = 0
        for bar in ax.axes.containers[0]:
            cur_width = bar.get_width()
            bar.set_width(bar_width_multiplier*cur_width)
            counter = counter + 1
    if hide_x_axis:
        ax.axes.xaxis.set_visible(False)
    if hide_y_axis:
        ax.axes.yaxis.set_visible(False)
    if x_margin != "auto":
        ax.margins(x=x_margin)
    if y_margin != "auto":
        ax.margins(y=y_margin)
    if grid:
        ax.grid()

    return ax
