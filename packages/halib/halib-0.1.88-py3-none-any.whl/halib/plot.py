from .common import now_str, norm_str, ConsoleLog
from .filetype import csvfile
from .system import filesys as fs
from functools import partial
from rich.console import Console
from rich.pretty import pprint
import click
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns


console = Console()
desktop_path = os.path.expanduser("~/Desktop")
REQUIRED_COLUMNS = ["epoch", "train_loss", "val_loss", "train_acc", "val_acc"]

import csv


def get_delimiter(file_path, bytes=4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter


# Function to verify that the DataFrame has the required columns, and only the required columns
def verify_csv(csv_file, required_columns=REQUIRED_COLUMNS):
    delimiter = get_delimiter(csv_file)
    df = pd.read_csv(csv_file, sep=delimiter)
    # change the column names to lower case
    df.columns = [col.lower() for col in df.columns]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"Required columns are: {REQUIRED_COLUMNS}, but found {df.columns}"
            )
    df = df[required_columns].copy()
    return df


def get_valid_tags(csv_files, tags):
    if tags is not None and len(tags) > 0:
        assert all(
            isinstance(tag, str) for tag in tags
        ), "tags must be a list of strings"
        assert all(
            len(tag) > 0 for tag in tags
        ), "tags must be a list of non-empty strings"
        valid_tags = tags
    else:
        valid_tags = []
        for csv_file in csv_files:
            file_name = fs.get_file_name(csv_file, split_file_ext=True)[0]
            tag = norm_str(file_name)
            valid_tags.append(tag)
    return valid_tags


def plot_ax(df, ax, metric="loss", tag=""):
    pprint(locals())
    # reset plt
    assert metric in ["loss", "acc"], "metric must be either 'loss' or 'acc'"
    part = ["train", "val"]
    for p in part:
        label = f"{tag}_{p}_{metric}"
        ax.plot(df["epoch"], df[f"{p}_{metric}"], label=label)
    return ax


def actual_plot_seaborn(frame, csv_files, axes, tags, log):
    # clear the axes
    for ax in axes:
        ax.clear()
    ls_df = []
    valid_tags = get_valid_tags(csv_files, tags)
    for csv_file in csv_files:
        df = verify_csv(csv_file)
        if log:
            with ConsoleLog(f"plotting {csv_file}"):
                csvfile.fn_display_df(df)
        ls_df.append(df)

    ls_metrics = ["loss", "acc"]
    for df_item, tag in zip(ls_df, valid_tags):
        # add tag to columns,excpet epoch
        df_item.columns = [
            f"{tag}_{col}" if col != "epoch" else col for col in df_item.columns
        ]
    # merge the dataframes on the epoch column
    df_combined = ls_df[0]
    for df_item in ls_df[1:]:
        df_combined = pd.merge(df_combined, df_item, on="epoch", how="outer")
    # csvfile.fn_display_df(df_combined)

    for i, metric in enumerate(ls_metrics):
        tags_str = "+".join(valid_tags) if len(valid_tags) > 1 else valid_tags[0]
        title = f"{tags_str}_{metric}-by-epoch"
        cols = [col for col in df_combined.columns if col != "epoch" and metric in col]
        cols = sorted(cols)
        # pprint(cols)
        plot_data = df_combined[cols]

        # line from same csv file (same tag) should have the same marker
        all_markers = [
            marker for marker in plt.Line2D.markers if marker and marker != " "
        ]
        tag2marker = {tag: marker for tag, marker in zip(valid_tags, all_markers)}
        plot_markers = []
        for col in cols:
            # find the tag:
            tag = None
            for valid_tag in valid_tags:
                if valid_tag in col:
                    tag = valid_tag
                    break
            plot_markers.append(tag2marker[tag])
        # pprint(list(zip(cols, plot_markers)))

        # create color
        sequential_palettes = [
            "Reds",
            "Greens",
            "Blues",
            "Oranges",
            "Purples",
            "Greys",
            "BuGn",
            "BuPu",
            "GnBu",
            "OrRd",
            "PuBu",
            "PuRd",
            "RdPu",
            "YlGn",
            "PuBuGn",
            "YlGnBu",
            "YlOrBr",
            "YlOrRd",
        ]
        # each csvfile (tag) should have a unique color
        tag2palette = {
            tag: palette for tag, palette in zip(valid_tags, sequential_palettes)
        }
        plot_colors = []
        for tag in valid_tags:
            palette = tag2palette[tag]
            total_colors = 10
            ls_colors = sns.color_palette(palette, total_colors).as_hex()
            num_part = len(ls_metrics)
            subarr = np.array_split(np.arange(total_colors), num_part)
            for idx, col in enumerate(cols):
                if tag in col:
                    chosen_color = ls_colors[
                        subarr[int(idx % num_part)].mean().astype(int)
                    ]
                    plot_colors.append(chosen_color)

        # pprint(list(zip(cols, plot_colors)))
        sns.lineplot(
            data=plot_data,
            markers=plot_markers,
            palette=plot_colors,
            ax=axes[i],
            dashes=False,
        )
        axes[i].set(xlabel="epoch", ylabel=metric, title=title)
        axes[i].legend()
        axes[i].grid()


def actual_plot(frame, csv_files, axes, tags, log):
    ls_df = []
    valid_tags = get_valid_tags(csv_files, tags)
    for csv_file in csv_files:
        df = verify_csv(csv_file)
        if log:
            with ConsoleLog(f"plotting {csv_file}"):
                csvfile.fn_display_df(df)
        ls_df.append(df)

    metric_values = ["loss", "acc"]
    for i, metric in enumerate(metric_values):
        for df_item, tag in zip(ls_df, valid_tags):
            metric_ax = plot_ax(df_item, axes[i], metric, tag)

        # set the title, xlabel, ylabel, legend, and grid
        tags_str = "+".join(valid_tags) if len(valid_tags) > 1 else valid_tags[0]
        metric_ax.set(
            xlabel="epoch", ylabel=metric, title=f"{tags_str}_{metric}-by-epoch"
        )
        metric_ax.legend()
        metric_ax.grid()


def plot_csv_files(
    csv_files,
    outdir="./out/plot",
    tags=None,
    log=False,
    save_fig=False,
    update_in_min=1,
):
    # if csv_files is a string, convert it to a list
    if isinstance(csv_files, str):
        csv_files = [csv_files]
    # if tags is a string, convert it to a list
    if isinstance(tags, str):
        tags = [tags]
    valid_tags = get_valid_tags(csv_files, tags)
    assert len(valid_tags) == len(
        csv_files
    ), "Unable to determine tags for each csv file"
    live_update_in_ms = int(update_in_min * 60 * 1000)
    fig, axes = plt.subplots(2, 1, figsize=(10, 17))
    if live_update_in_ms:  # live update in min should be > 0
        from matplotlib.animation import FuncAnimation

        anim = FuncAnimation(
            fig,
            partial(
                actual_plot_seaborn, csv_files=csv_files, axes=axes, tags=tags, log=log
            ),
            interval=live_update_in_ms,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()
    else:
        actual_plot_seaborn(None, csv_files, axes, tags, log)
        plt.show()

    if save_fig:
        os.makedirs(outdir, exist_ok=True)
        tags_str = "+".join(valid_tags) if len(valid_tags) > 1 else valid_tags[0]
        tag = f"{now_str()}_{tags_str}"
        fig.savefig(f"{outdir}/{tag}_plot.png")
        enable_plot_pgf()
        fig.savefig(f"{outdir}/{tag}_plot.pdf")
    if live_update_in_ms:
        return anim


def enable_plot_pgf():
    matplotlib.use("pdf")
    matplotlib.rcParams.update(
        {
            "pgf.texsystem": "pdflatex",
            "font.family": "serif",
            "text.usetex": True,
            "pgf.rcfonts": False,
        }
    )


def save_fig_latex_pgf(filename, directory="."):
    enable_plot_pgf()
    if ".pgf" not in filename:
        filename = f"{directory}/{filename}.pgf"
    plt.savefig(filename)


# https: // click.palletsprojects.com/en/8.1.x/api/
@click.command()
@click.option("--csvfiles", "-f", multiple=True, type=str, help="csv files to plot")
@click.option(
    "--outdir",
    "-o",
    type=str,
    help="output directory for the plot",
    default=str(desktop_path),
)
@click.option(
    "--tags", "-t", multiple=True, type=str, help="tags for the csv files", default=[]
)
@click.option("--log", "-l", is_flag=True, help="log the csv files")
@click.option("--save_fig", "-s", is_flag=True, help="save the plot as a file")
@click.option(
    "--update_in_min",
    "-u",
    type=float,
    help="update the plot every x minutes",
    default=0.0,
)
def main(
    csvfiles,
    outdir,
    tags,
    log,
    save_fig,
    update_in_min,
):
    plot_csv_files(list(csvfiles), outdir, list(tags), log, save_fig, update_in_min)


if __name__ == "__main__":
    main()
