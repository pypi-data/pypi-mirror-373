import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox
from lukhed_basic_utils import matplotlibBasics, matplotlibFormatting

def draw_football_field(formation='shotgun', player_image_fill=None, circle_image_zooms=0.1, show_plot=False,
                        save_image=None, twitter_resize=True, x_margin=0.01, y_margin=0.1):
    """

    :param y_margin:
    :param x_margin:
    :param save_image:
    :param show_plot:
    :param circle_image_zooms:
    :param formation:
    :param player_image_fill:
    :return:
    """

    default_player_image_fill = {
            "c": None,
            "rg": None,
            "lg": None,
            "rt": None,
            "lt": None,
            "te1": None,
            "te2": None,
            "qb": None,
            "wr1": None,
            "wr2": None,
            "wr3": None,
            "wr4": None,
            "wr5": None,
            "rb1": None,
            "rb2": None,
            "fb": None
        }

    if player_image_fill is not None:
        for key in player_image_fill:
            default_player_image_fill[key] = player_image_fill[key]

    player_image_fill = default_player_image_fill

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(16, 9))

    # Set the field dimensions
    field_width = 60
    field_length = 30  # yards (partial field)

    # Draw the field
    ax.set_xlim(0, field_width)
    ax.set_ylim(0, field_length)
    ax.set_facecolor('#4CAF50')  # Green field color

    # Draw yard lines
    for i in range(0, int(field_length), 5):
        ax.axhline(y=i, color='white', linestyle='-', linewidth=1, zorder=5)

    # Function to draw a player
    def draw_player(x, y, number, color='red', image_path=None):
        if image_path:
            img = matplotlibBasics.get_image(image_path, plt, circle_image_zooms)
            ab = AnnotationBbox(img, (x, y), frameon=False, zorder=6)
            ax.add_artist(ab)
        else:
            circle = plt.Circle((x, y), 1.8, fill=True, color=color, zorder=6)
            ax.add_artist(circle)
            ax.text(x, y, str(number), ha='center', va='center', color='white', fontweight='bold', zorder=6)


    # Draw the offensive line
    draw_player(30, 13, 'C', image_path=player_image_fill['c'])  # Center
    draw_player(35, 13, 'RG', image_path=player_image_fill['rg'])  # Right Guard
    draw_player(25, 13, 'LG', image_path=player_image_fill['lg'])  # Left Guard
    draw_player(40, 13, 'RT', image_path=player_image_fill['rt'])  # Right Tackle
    draw_player(20, 13, 'LT', image_path=player_image_fill['lt'])  # Left Tackle

    # Draw offensive lineup (example: Pro Set formation)
    if formation == 'shotgun':
        draw_player(45, 13, 'TE', image_path=player_image_fill['te1'])  # Tight End
        draw_player(30, 6, 'QB', image_path=player_image_fill['qb'])  # Quarterback
        draw_player(35, 6, 'RB', image_path=player_image_fill['rb1'])  # Running Back
        draw_player(57, 10.5, 'WR', image_path=player_image_fill['wr1'])  # Wide Receiver Right
        draw_player(3, 13, 'WR', image_path=player_image_fill['wr2'])  # Wide Receiver Left
        draw_player(8, 10.5, 'WR', image_path=player_image_fill['wr3'])  # Wide Receiver Left Slot


    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add title
    plt.title(f'{formation.title()} Formation', fontsize=24)

    plt.tight_layout()


    if twitter_resize:
        ax = matplotlibFormatting.resize_plot_for_twitter(ax)

    # Format the bar chart
    ax = matplotlibFormatting.adjust_margins(ax, x_margin=x_margin, y_margin=y_margin)

    if show_plot:
        plt.show()
    if save_image is not None:
        fig.savefig(save_image)

    return {
        "fig": fig,
        "ax": ax,
        "imgLocation": save_image,
        "plt": plt
    }

def main():
    draw_football_field(show_plot=True)


if __name__ == '__main__':
    main()
