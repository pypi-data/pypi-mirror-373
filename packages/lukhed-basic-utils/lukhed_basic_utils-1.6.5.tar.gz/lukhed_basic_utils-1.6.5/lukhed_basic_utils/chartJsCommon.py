from lukhed_basic_utils import listWorkCommon as lC
import random


def create_line_chart(x_axis_list=None, y_axis_lists=None, y_labels=None, line_label_border_colors=None,
                      point_bg_color=None, point_radii=None, additional_data=None):
    """
    Creates a line chart json compatible with chartJs

    :param x_axis_list:                 list() or None, list of x axis labels. If None is provided, defaults to a list
                                        of numbers.

                                        starting example: [Jan, Feb, March, April]

    :param y_axis_lists:                list() or None, list or list of list containing the y values for the lines
                                        you want to plot. If multiple lines, it should be a list of lists,
                                        with each list containing the y data for a line. Note, the y data in each
                                        list should correspond 1 to 1 with the x axis list. If None is provided, a
                                        simple, randomly generated dataset will be utilized.

                                        example cont., 2 lines on the x axis: [[1,2,3,4], [2,4,6,8]]

    :param y_labels:                    list() or None, Each data set provided in y_axis_list should have a label. If
                                        None, then a string "line + #" will be used.

                                        example cont: [line 1, line 2]

    :param line_label_border_colors:    list() or None, list of colors to be associated with each line. In chart js
                                        the line color is the same as the legend label border color.

                                        example cont: [red, blue]

    :param point_bg_color:              list() or None, list of colors to be associated with the point colors of each
                                        line. In chartjs, the point color can be a different color than the line. This
                                        point color is also the main "bg color" of the label in the legend.
                                        Note: this is not a color for each point, but a color for each line whose
                                        points will be of this color.

                                        If None is provided, then the point will be
                                        the same as the line color

    :param point_radii                  None or list(). List must correspond to
                                            Each point can be assigned one value (use int),
                                            Assign every point its own value (use list)
                                            None, it will be default chartJS value


    :param additional_data:             dict(), any additional data you want as a separate dict
                                        to be available with your chart

    :return:                            dict(), json for the chart.js is found in key "chartData"
    """

    if y_axis_lists is None:
        # randomly generate y axis data of length 7
        y_axis_lists = list()
        i = 0
        while i < 7:
            n = random.randint(1, 10)
            y_axis_lists.append(n)
            i = i + 1

    if type(y_axis_lists[0]) is not list:
        y_axis_lists = [y_axis_lists]

    if x_axis_list is None:
        x_axis_list = list()
        i = 0
        while i < len(y_axis_lists[0]):
            x_axis_list.append(i)
            i = i + 1

    if y_labels is None:
        y_labels = list()
        i = 1
        while i < len(y_axis_lists) + 1:
            y_labels.append("line " + str(i))
            i = i + 1

    if line_label_border_colors is None:
        line_label_border_colors = lC.create_list_of_colors(len(y_axis_lists))

    if point_bg_color is None:
        point_bg_color = line_label_border_colors.copy()

    if point_radii is None:
        point_radii = len(y_axis_lists)*[3]
    else:
        point_radii = point_radii

    data_sets = []
    counter = 0
    for line in y_axis_lists:
        temp_dict = {
            "label": y_labels[counter],
            "data": line.copy(),
            "pointRadius": point_radii[counter],
            "borderColor": line_label_border_colors[counter],
            "backgroundColor": point_bg_color[counter]
        }
        data_sets.append(temp_dict.copy())
        counter = counter + 1

    op_dict = {"chartData": {"labels": x_axis_list, "datasets": data_sets},
               "additionalData": additional_data}

    return op_dict


def create_bar_chart_stacked_grouped(x_axis_list=None, bar_list=None, bar_stacks_list=None, bar_stacks_colors=None,
                                     stack_value_dict=None, orientation="default", additional_data=None):
    """
    Creates json for stacked barchart compatible with chartJs

    :param x_axis_list: list(), 
        Each value in the list corresponds to a x-axis value, one of each corresponding to one
        group of stacked bars. Starting example, dk salary compare for all nfl matchups. x_axis_list
        would be each mach up ["CAR @ DET", "SEA @ LAR", ...]

    :param bar_list: list() 
        of strings, list corresponding to the bars available at each x axis point. Continuing 
        example, the bars needed for each matchup would be two teams. [team1, team2]

    :param bar_stacks_list: list(), 
        list corresponding to the stacks that make up each bar. Continuing the example,
        each team bar is consisting of the salaries for each position ["QB", "RB1" "RB2"...]

    :param bar_stacks_colors: list(), 
        colors for each stack in the stack list. Hex values

    :param stack_value_dict: dict(), 
        the bar list values are used as keys to retrieve stack values across all axis
        points for a common bar group. Note, the stack value list has a 1 to 1 mapping to the
        x axis. Continuing the example
            {
            "team1":                                Two bars at each x point, so two main keys
            {
                "QB": [$7550, $6500, ..],           Each bar has a position which is a sub key
                "RB1": [],                          Each position has a list of salary values
                "RB2": []                           The salary values correspond directly to x-axis
            },                                      Which in this case is a matchup.
        "team2":                                    So QB[0], is match-up 0, qb[1] is match-up 1
            {                                       etc.
                "QB": [],
                "RB1": [],
                "RB2": []
                }
        }

    :param orientation: str(), 
        'vertical' or 'horizontal', default is 'vertical' corresponding to vertical bars
    :param additional_data: dict(), Optional,
        allows you to provide more data to be included in the json, for use in
        in custom tooltips/legends etc. It is accessible in the final json in key "additionalData"

    :return: dict(), json for the chart.js is found in key "chartData"
    """

    if x_axis_list is None:
        raise Exception("'x_axis_list' is a required argument")
    if bar_stacks_list is None:
        raise Exception("'bar_stacks_list' is a required argument")
    if bar_list is None:
        raise Exception("'bar_list' is a required argument")
    if stack_value_dict is None:
        raise Exception("'stack_value_dict' is a required argument")
    if bar_stacks_colors is None:
        raise Exception("'bar_stacks_colors' is a required argument")
    if additional_data is None:
        additional_data = {}

    # For each bar
    data_list = list()
    a = 0
    while a < len(bar_list):

        bar_name = bar_list[a]

        b = 0
        while b < len(bar_stacks_list):
            temp_dict = dict()
            temp_dict["label"] = bar_stacks_list[b]
            temp_dict["data"] = stack_value_dict[bar_name][bar_stacks_list[b]]
            temp_dict["backgroundColor"] = bar_stacks_colors[b]
            temp_dict["stack"] = bar_name
            b = b + 1
            data_list.append(temp_dict.copy())

        a = a + 1

    return {
        "chartData": {
            "labels": x_axis_list,
            "datasets": data_list
        },
        "additionalData": additional_data
    }


def create_bar_chart_simple(x_axis_list=None, y_axis_lists=None, y_labels=None, bar_colors=None, additional_data=None):
    """
    :param x_axis_list:                 list() or None, list of x axis labels. If None is provided, defaults to a list
                                        of numbers.

                                        starting example: [Jan, Feb, March, April]

    :param y_axis_lists:                list() or None, list or list of list containing the y values for the bars
                                        you want to plot. If multiple bars at each x, it should be a list of lists,
                                        with each list containing the y data for the bar. Note, the y data in each
                                        list should correspond 1 to 1 with the x axis list. If None is provided, a
                                        simple, randomly generated dataset will be utilized.

                                        example cont., 2 bars on the x axis: [[1,2,3,4], [2,4,6,8]]

    :param y_labels:                    list() or None, Each data set provided in y_axis_list should have a label. If
                                        None, then a string "bar + #" will be used.

                                        example cont: [bar 1, bar 2]

    :param bar_colors:                  list() or None, list of colors to be associated with each bar. In chart js
                                        the bar color is the same as the legend label border color.

                                        example cont: [red, blue]

    :param additional_data:             dict(), any additional data you want as a separate dict
                                        to be available with your chart

    :return:                            dict(), json for the chart.js is found in key "chartData"
    """
    if y_axis_lists is None:
        # randomly generate y axis data of length 7
        y_axis_lists = list()
        i = 0
        while i < 7:
            n = random.randint(1, 10)
            y_axis_lists.append(n)
            i = i + 1

    if type(y_axis_lists[0]) is not list:
        y_axis_lists = [y_axis_lists]

    if x_axis_list is None:
        x_axis_list = list()
        i = 0
        while i < len(y_axis_lists[0]):
            x_axis_list.append("bar " + str(i))
            i = i + 1

    if y_labels is None:
        y_labels = list()
        i = 1
        while i < len(y_axis_lists) + 1:
            y_labels.append("bar " + str(i))
            i = i + 1

    if bar_colors is None:
        bar_colors = lC.create_list_of_colors(len(y_axis_lists))

    data_sets = []
    counter = 0
    for bar in y_axis_lists:
        temp_dict = {
            "label": y_labels[counter],
            "data": bar.copy(),
            "borderColor": bar_colors[counter],
            "backgroundColor": bar_colors[counter]
        }
        data_sets.append(temp_dict.copy())
        counter = counter + 1

    op_dict = {"chartData": {"labels": x_axis_list, "datasets": data_sets},
               "additionalData": additional_data}

    return op_dict


def create_doughnut_chart(data_values_list=None, data_labels=None, slice_colors=None,
                          additional_data=None):
    data_values_list = parse_core_value_list(data_values_list)
    data_labels = parse_labels(data_values_list, data_labels)
    slice_colors = parse_core_color_list(data_values_list, slice_colors)

    chart_dict = {
        "labels": data_labels,
        "datasets": [{"label": "Dataset 1", "data": data_values_list, "backgroundColor": slice_colors}]
    }

    return {
        "chartData": chart_dict,
        "additionalData": additional_data
    }


def create_bubble_chart(x_axis_list=None, y_axis_list=None, radius_list=None, data_set_label=None,
                        bubble_colors=None, bubble_border_colors=None, additional_data=None):
    """
        Note: If there is a choice to use different color bubbles within the same data set, you will want to turn
        the legend off via the config constant which is set up on the javascript side.

        Note 2: This function does not support multiple bubble data sets (just one set for now)


        :param x_axis_list:                 list() or None, list of x axis points. If None is provided,
                                            defaults to a list of numbers is provided. Note this must correspond
                                            1 to 1 with the y_axis_list to form points.

                                            starting example: [1, 2 ,3 ,4]

        :param y_axis_list:                 list() or None, list containing the y value for the bubbles
                                            you want to plot. Note, the y data in the list should correspond 1 to 1
                                            with the x axis list. If None is provided, a simple, randomly generated
                                            dataset will be utilized.

                                            example cont.,: [1,2,3,4]

        :param radius_list:                 list() or None, list containing the radius value for each bubble. Note,
                                            this list should correspond 1 to 1 with each point provided via the x-list
                                            and y-list parameters.

                                            example cont.: [10, 15, 20, 30]

        :param data_set_label:              str() or None, Each data set provided in y_axis_list should have a label.
                                            If None, then a string "Bubble Set" will be used.

                                            example cont: [Games]

        :param bubble_colors:               list() or None, list of colors to be associated with each bubble. By
                                            default, red bubbles are created. Note that if providing more than one
                                            color, the data set legend will have the color of the first bubble, so
                                            you may want to hide the legend via frontend.

                                            example cont: [red, blue]

                                            Javascript side:
                                            const config = {
                                                type: 'bubble',
                                                data: data,             ->>> output of this function goes here.
                                                options: {
                                                    plugins: {
                                                        legend: {
                                                            display: false
                                                        }
                                                    }
                                                }
                                            };

        :param bubble_border_colors:        list() or None, by default, this will be same color as background color.

                                            example cont: [black, black]

        :param additional_data:             dict(), any additional data you want as a separate dict
                                            to be available with your chart

        :return:                            dict(), json for the chart.js is found in key "chartData"
        """

    if y_axis_list is None:
        # randomly generate y axis data of length 7
        y_axis_list = list()
        i = 0
        while i < 7:
            n = random.randint(1, 10)
            y_axis_list.append(n)
            i = i + 1

    if radius_list is None:
        # randomly generate radius sizes for 7 points
        radius_list = list()
        i = 0
        while i < 7:
            n = random.randint(1, 40)
            radius_list.append(n)
            i = i + 1

    if x_axis_list is None:
        # add to x axis list points from 0 to 6
        x_axis_list = list()
        i = 0
        while i < len(y_axis_list):
            x_axis_list.append(i)
            i = i + 1

    if data_set_label is None:
        data_set_label = "Bubble Set"

    if bubble_colors is None:
        bubble_colors = ["red"] * len(y_axis_list)

    if bubble_border_colors is None:
        bubble_border_colors = bubble_colors.copy()

    data_sets = []
    counter = 0

    bubble_data = []
    i = 0
    while i < len(y_axis_list):
        bubble_data.append({
            "x": x_axis_list[i],
            "y": y_axis_list[i],
            "r": radius_list[i]
        })
        i = i + 1

    temp_dict = {
        "label": data_set_label,
        "data": bubble_data,
        "borderColor": bubble_border_colors,
        "backgroundColor": bubble_colors
    }

    data_sets.append(temp_dict.copy())

    op_dict = {"chartData": {"datasets": data_sets},
               "additionalData": additional_data}

    return op_dict


def create_scatter_chart(x_axis_list=None, y_axis_list=None, data_set_label=None,
                         point_bg_colors=None, point_outline_colors=None, additional_data=None, point_radius=None,
                         point_style="circle", point_border_width=None, hover_radius=None):
    """


        :param x_axis_list:                 list() or None, list of x axis points. If None is provided,
                                            defaults to a list of numbers is provided. Note this must correspond
                                            1 to 1 with the y_axis_list to form points.

                                            starting example: [1, 2 ,3 ,4]

        :param y_axis_list:                 list() or None, list containing the y value for the bubbles
                                            you want to plot. Note, the y data in the list should correspond 1 to 1
                                            with the x axis list. If None is provided, a simple, randomly generated
                                            dataset will be utilized.

                                            example cont.,: [1,2,3,4]


        :param data_set_label:              str() or None, Each data set provided in y_axis_list should have a label.
                                            If None, then a string "Bubble Set" will be used.

                                            example cont: [Games]

        :param point_bg_colors:             list() or None, list of colors to be associated with each point. By
                                            default, red bubbles are created. Note that if providing more than one
                                            color, the data set legend will have the color of the first bubble, so
                                            you may want to hide the legend via frontend.

                                            example cont: [red, blue]
                                            Note: You can achieve transparency with: 'rgba(0, 0, 0, 0.0)'

                                            Javascript side:
                                            const config = {
                                                type: 'scatter',
                                                data: data,             ->>> output of this function goes here.
                                                options: {
                                                    plugins: {
                                                        legend: {
                                                            display: false
                                                        }
                                                    }
                                                }
                                            };

        :param point_outline_colors:        list() or None, list of colors for the point

        :param point_radius:                int(), size of the points in the set

        :param point_style:                 str():
                                                'circle'
                                                'cross'
                                                'crossRot'
                                                'dash'
                                                'line'
                                                'rect'
                                                'rectRounded'
                                                'rectRot'
                                                'star'
                                                'triangle'

        :param point_border_width:          int(), this is the width of the line of the point.


        :param additional_data:             dict(), any additional data you want as a separate dict
                                            to be available with your chart

        :return:                            dict(), json for the chart.js is found in key "chartData"
        """

    if y_axis_list is None:
        # randomly generate y axis data of length 7
        y_axis_list = list()
        i = 0
        while i < 7:
            n = random.randint(1, 10)
            y_axis_list.append(n)
            i = i + 1

    if x_axis_list is None:
        # add to x axis list points from 0 to 6
        x_axis_list = list()
        i = 0
        while i < len(y_axis_list):
            x_axis_list.append(i)
            i = i + 1

    if data_set_label is None:
        data_set_label = "Scatter Dataset"

    if point_bg_colors is None:
        point_bg_colors = ["red"] * len(y_axis_list)

    if point_outline_colors is None:
        point_outline_colors = ["black"] * len(y_axis_list)

    if point_radius is None:
        point_radius = 10

    if point_border_width is None:
        point_border_width = 3

    if hover_radius is None:
        hover_radius = 4

    data_sets = []

    scatter_data = []
    i = 0
    while i < len(y_axis_list):
        scatter_data.append({
            "x": x_axis_list[i],
            "y": y_axis_list[i]
        })
        i = i + 1

    temp_dict = {
        "label": data_set_label,
        "type": "scatter",
        "data": scatter_data,
        "backgroundColor": point_bg_colors,
        "borderColor": point_outline_colors,
        "pointRadius": point_radius,
        "pointStyle": point_style,
        "hoverRadius": hover_radius,
        "pointBorderWidth": point_border_width
    }

    data_sets.append(temp_dict.copy())

    op_dict = {"chartData": {"datasets": data_sets},
               "additionalData": additional_data}

    return op_dict


def parse_labels(value_list, corresponding_labels):
    """
    Labels are optionally provided with each chart type. Use this function to parse a label input. If None is provided
    by the user, then this function generates label list.

    :param value_list: list(), the set of values that need labels
    :param corresponding_labels: list() or None, the label parameter provided by the end user.
    :return: list(), list of labels. If labels were provided by end user, just return the list. If not, labels are
             generated for the list. "data 1", "data 2", etc.
    """

    labels_list = list()
    if corresponding_labels is None:
        i = 1
        while i < len(value_list) + 1:
            labels_list.append("data " + str(i))
            i = i + 1
    else:
        labels_list = corresponding_labels

    return labels_list


def parse_core_value_list(value_list):
    """
    Each chart js function allows a user to call the function without inputting any parameter. In this case, we create
    a random chart. This allows them to the output of the function, or create a placeholder chart easily.

    This function parses the users core value list (i.e. the values of the chart that are essential to make a chart)

    :param value_list: list() or None. If there is a list of values, this function just returns back the list. If None,
                       this function creates a random list of values between 1 and 10 and of length 7.
    :return:
    """

    op_list = list()
    if value_list is None:
        # randomly generate y axis data of length 7

        i = 0
        while i < 7:
            n = random.randint(1, 10)
            op_list.append(n)
            i = i + 1
    else:
        op_list = value_list

    return op_list


def parse_core_color_list(values_list, core_colors_list):
    """
    Each graph has a core color for data points (line color, pie slice color, bar color). If none is provided, this
    function will generate colors.

    :param values_list:
    :param core_colors_list:
    :return:
    """

    op_list = list()
    if core_colors_list is None:
        op_list = lC.create_list_of_colors(len(values_list))
    else:
        op_list = core_colors_list

    return op_list

