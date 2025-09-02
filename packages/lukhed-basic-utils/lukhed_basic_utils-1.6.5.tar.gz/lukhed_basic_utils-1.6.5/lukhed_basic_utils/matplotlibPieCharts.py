from lukhed_basic_utils import matplotlibBasics, mathCommon as mC
from matplotlib.offsetbox import AnnotationBbox


def pie_chart_with_images_as_labels(sizes, labels, image_list, image_zoom="auto", show_image=False, save_image=None,
                                    colors=None, explode=None, shadow=False, startangle=90,
                                    image_y_offset=0, image_x_offset=0, hide_legend=False):
    """
    Creates a pie chart with images as labels.

    Parameters:
    - sizes (list of float): Sizes of the pie slices.
    - labels (list of str): Labels for the pie slices.
    - image_list (list of str): List of file paths to images for each pie slice.
    - image_zoom (float or str): Zoom level for images; 'auto' adjusts based on number of slices.
    - show_image (bool): Whether to show the plot.
    - save_image (str): Path to save the plot.
    - colors (list of str): Colors for the pie slices.
    - explode (list of float): Fraction of the radius to offset each slice.
    - shadow (bool): Whether to add a shadow to the pie chart.
    - startangle (float): Starting angle for the pie chart.
    - image_y_offset (float): Vertical offset for images.
    - image_x_offset (float): Horizontal offset for images.
    - hide_legend (bool): Whether to hide the legend.

    Returns:
    - dict: Contains the figure and axes objects, and the path to the saved image.
    """
    plt = matplotlibBasics.get_plt()
    np = mC.get_np()
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust size as needed

    if image_zoom == "auto":
        if len(sizes) <= 5:
            image_zoom = .3
        else:
            image_zoom = 1

    # Plot pie chart
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, explode=explode,
                                      shadow=shadow, startangle=startangle, autopct='%1.1f%%')

    # Add images on the pie chart
    for wedge, image_path in zip(wedges, image_list):
        # Get wedge center
        angle = (wedge.theta2 + wedge.theta1) / 2
        radius = wedge.r
        x_center = radius * np.cos(np.radians(angle))
        y_center = radius * np.sin(np.radians(angle))

        # Adjust position for images
        ab = AnnotationBbox(matplotlibBasics.get_image(image_path, plt, image_zoom),
                            (x_center + image_x_offset, y_center + image_y_offset),
                            frameon=False)
        ax.add_artist(ab)

    # Hide legend if requested
    if hide_legend:
        ax.legend_.remove()

    if show_image:
        plt.show()
    if save_image is not None:
        fig.savefig(save_image)

    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": save_image
    }

