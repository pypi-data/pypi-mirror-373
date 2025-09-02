from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

# List of colors
# ! https://rich.readthedocs.io/en/stable/appendix/colors.html
all_colors = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
    "grey0",
    "navy_blue",
    "dark_blue",
    "blue3",
    "blue1",
    "dark_green",
    "deep_sky_blue4",
    "dodger_blue3",
    "dodger_blue2",
    "green4",
    "spring_green4",
    "turquoise4",
    "deep_sky_blue3",
    "dodger_blue1",
    "dark_cyan",
    "light_sea_green",
    "deep_sky_blue2",
    "deep_sky_blue1",
    "green3",
    "spring_green3",
    "cyan3",
    "dark_turquoise",
    "turquoise2",
    "green1",
    "spring_green2",
    "spring_green1",
    "medium_spring_green",
    "cyan2",
    "cyan1",
    "purple4",
    "purple3",
    "blue_violet",
    "grey37",
    "medium_purple4",
    "slate_blue3",
    "royal_blue1",
    "chartreuse4",
    "pale_turquoise4",
    "steel_blue",
    "steel_blue3",
    "cornflower_blue",
    "dark_sea_green4",
    "cadet_blue",
    "sky_blue3",
    "chartreuse3",
    "sea_green3",
    "aquamarine3",
    "medium_turquoise",
    "steel_blue1",
    "sea_green2",
    "sea_green1",
    "dark_slate_gray2",
    "dark_red",
    "dark_magenta",
    "orange4",
    "light_pink4",
    "plum4",
    "medium_purple3",
    "slate_blue1",
    "wheat4",
    "grey53",
    "light_slate_grey",
    "medium_purple",
    "light_slate_blue",
    "yellow4",
    "dark_sea_green",
    "light_sky_blue3",
    "sky_blue2",
    "chartreuse2",
    "pale_green3",
    "dark_slate_gray3",
    "sky_blue1",
    "chartreuse1",
    "light_green",
    "aquamarine1",
    "dark_slate_gray1",
    "deep_pink4",
    "medium_violet_red",
    "dark_violet",
    "purple",
    "medium_orchid3",
    "medium_orchid",
    "dark_goldenrod",
    "rosy_brown",
    "grey63",
    "medium_purple2",
    "medium_purple1",
    "dark_khaki",
    "navajo_white3",
    "grey69",
    "light_steel_blue3",
    "light_steel_blue",
    "dark_olive_green3",
    "dark_sea_green3",
    "light_cyan3",
    "light_sky_blue1",
    "green_yellow",
    "dark_olive_green2",
    "pale_green1",
    "dark_sea_green2",
    "pale_turquoise1",
    "red3",
    "deep_pink3",
    "magenta3",
    "dark_orange3",
    "indian_red",
    "hot_pink3",
    "hot_pink2",
    "orchid",
    "orange3",
    "light_salmon3",
    "light_pink3",
    "pink3",
    "plum3",
    "violet",
    "gold3",
    "light_goldenrod3",
    "tan",
    "misty_rose3",
    "thistle3",
    "plum2",
    "yellow3",
    "khaki3",
    "light_yellow3",
    "grey84",
    "light_steel_blue1",
    "yellow2",
    "dark_olive_green1",
    "dark_sea_green1",
    "honeydew2",
    "light_cyan1",
    "red1",
    "deep_pink2",
    "deep_pink1",
    "magenta2",
    "magenta1",
    "orange_red1",
    "indian_red1",
    "hot_pink",
    "medium_orchid1",
    "dark_orange",
    "salmon1",
    "light_coral",
    "pale_violet_red1",
    "orchid2",
    "orchid1",
    "orange1",
    "sandy_brown",
    "light_salmon1",
    "light_pink1",
    "pink1",
    "plum1",
    "gold1",
    "light_goldenrod2",
    "navajo_white1",
    "misty_rose1",
    "thistle1",
    "yellow1",
    "light_goldenrod1",
    "khaki1",
    "wheat1",
    "cornsilk1",
    "grey100",
    "grey3",
    "grey7",
    "grey11",
    "grey15",
    "grey19",
    "grey23",
    "grey27",
    "grey30",
    "grey35",
    "grey39",
    "grey42",
    "grey46",
    "grey50",
    "grey54",
    "grey58",
    "grey62",
    "grey66",
    "grey70",
    "grey74",
    "grey78",
    "grey82",
    "grey85",
    "grey89",
    "grey93",
]

basic_colors = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
]

def rcolor_all_str():
    pprint(all_colors)

def rcolor_basic_str():
    pprint(basic_colors)

def rcolor_str(in_str, color="white"):
    assert color in all_colors, f"color must be one of {all_colors}"
    return f"[{color}]{in_str}[/{color}]"

def rcolor_palette(color_list):
    # make sure all colors are valid (in all_colors)
    for color in color_list:
        assert (
            color in all_colors
        ), f"color must be a valid color. call <rcolor_all_str()> or <rcolor_palette_all()> to see all valid colors"
    # Initialize console
    console = Console()

    # Create a table with horizontal lines and six columns
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)

    # Define the columns
    table.add_column("Color Name 1", style="bold")
    table.add_column("Sample 1", style="bold")
    table.add_column("Color Name 2", style="bold")
    table.add_column("Sample 2", style="bold")
    table.add_column("Color Name 3", style="bold")
    table.add_column("Sample 3", style="bold")

    # Adjust the number of rows needed for the table
    num_colors = len(color_list)
    num_rows = (num_colors + 2) // 3  # Ceiling division to ensure all colors fit

    # Add rows to the table
    for i in range(num_rows):
        color1 = color_list[i * 3] if i * 3 < num_colors else ""
        color2 = color_list[i * 3 + 1] if i * 3 + 1 < num_colors else ""
        color3 = color_list[i * 3 + 2] if i * 3 + 2 < num_colors else ""
        filled_rect1 = Text(" " * 10, style=f"on {color1}") if color1 else ""
        filled_rect2 = Text(" " * 10, style=f"on {color2}") if color2 else ""
        filled_rect3 = Text(" " * 10, style=f"on {color3}") if color3 else ""
        table.add_row(color1, filled_rect1, color2, filled_rect2, color3, filled_rect3)

    # Print the table
    console.print(table)

def rcolor_palette_basic():
    rcolor_palette(basic_colors)

def rcolor_palette_all():
    rcolor_palette(all_colors)
