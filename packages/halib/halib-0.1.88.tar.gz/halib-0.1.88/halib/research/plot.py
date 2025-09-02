import os
import pandas as pd
import plotly.express as px
from rich.console import Console
from ..common import now_str, norm_str, ConsoleLog
from ..filetype import csvfile
from ..system import filesys as fs
import click
import time

import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
from typing import Callable, Optional, Tuple, List, Union


console = Console()
desktop_path = os.path.expanduser("~/Desktop")

class PlotHelper:
    def _verify_csv(self, csv_file):
        """Read a CSV and normalize column names (lowercase)."""
        try:
            df = csvfile.read_auto_sep(csv_file)
            df.columns = [col.lower() for col in df.columns]
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{csv_file}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file '{csv_file}': {str(e)}")

    @staticmethod
    def _norm_str(s):
        """Normalize string by converting to lowercase and replacing spaces/underscores."""
        return s.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _get_file_name(file_path):
        """Extract file name without extension."""
        return os.path.splitext(os.path.basename(file_path))[0]

    def _get_valid_tags(self, csv_files, tags):
        """Generate tags from file names if not provided."""
        if tags:
            return list(tags)
        return [self._norm_str(self._get_file_name(f)) for f in csv_files]

    def _prepare_long_df(self, csv_files, tags, x_col, y_cols, log=False):
        """Convert multiple CSVs into a single long-form dataframe for Plotly."""
        dfs = []
        for csv_file, tag in zip(csv_files, tags):
            df = self._verify_csv(csv_file)
            # Check columns
            if x_col not in df.columns:
                raise ValueError(f"{csv_file} is missing x_col '{x_col}'")
            missing = [c for c in y_cols if c not in df.columns]
            if missing:
                raise ValueError(f"{csv_file} is missing y_cols {missing}")

            if log:
                console.log(f"Plotting {csv_file}")
                console.print(df)

            # Wide to long
            df_long = df.melt(
                id_vars=x_col,
                value_vars=y_cols,
                var_name="metric_type",
                value_name="value",
            )
            df_long["tag"] = tag
            dfs.append(df_long)

        return pd.concat(dfs, ignore_index=True)

    def _plot_with_plotly(
        self,
        df_long,
        tags,
        outdir,
        save_fig,
        out_fmt="svg",
        font_size=16,
        x_col="epoch",
        y_cols=None,
    ):
        """Generate Plotly plots for given metrics."""
        assert out_fmt in ["svg", "pdf", "png"], "Unsupported format"
        if y_cols is None:
            raise ValueError("y_cols must be provided")

        # Group by suffix (e.g., "loss", "acc") if names like train_loss exist
        metric_groups = sorted(set(col.split("_")[-1] for col in y_cols))

        for metric in metric_groups:
            subset = df_long[df_long["metric_type"].str.contains(metric)]

            if out_fmt == "svg":  # LaTeX-style
                title = f"${'+'.join(tags)}\\_{metric}\\text{{-by-{x_col}}}$"
                xaxis_title = f"$\\text{{{x_col.capitalize()}}}$"
                yaxis_title = f"${metric.capitalize()}$"
            else:
                title = f"{'+'.join(tags)}_{metric}-by-{x_col}"
                xaxis_title = x_col.capitalize()
                yaxis_title = metric.capitalize()

            fig = px.line(
                subset,
                x=x_col,
                y="value",
                color="tag",
                line_dash="metric_type",
                title=title,
            )
            fig.update_layout(
                font=dict(family="Computer Modern", size=font_size),
                xaxis_title=xaxis_title,
                yaxis_title=yaxis_title,
            )
            fig.show()

            if save_fig:
                os.makedirs(outdir, exist_ok=True)
                timestamp = now_str()
                filename = f"{timestamp}_{'+'.join(tags)}_{metric}"
                try:
                    fig.write_image(os.path.join(outdir, f"{filename}.{out_fmt}"))
                except Exception as e:
                    console.log(f"Error saving figure '{filename}.{out_fmt}': {str(e)}")

    @classmethod
    def plot_csv_timeseries(
        cls,
        csv_files,
        outdir="./out/plot",
        tags=None,
        log=False,
        save_fig=False,
        update_in_min=0,
        out_fmt="svg",
        font_size=16,
        x_col="epoch",
        y_cols=["train_loss", "train_acc"],
    ):
        """Plot CSV files with Plotly, supporting live updates, as a class method."""
        if isinstance(csv_files, str):
            csv_files = [csv_files]
        if isinstance(tags, str):
            tags = [tags]

        if not y_cols:
            raise ValueError("You must specify y_cols explicitly")

        # Instantiate PlotHelper to call instance methods
        plot_helper = cls()
        valid_tags = plot_helper._get_valid_tags(csv_files, tags)
        assert len(valid_tags) == len(
            csv_files
        ), "Number of tags must match number of CSV files"

        def run_once():
            df_long = plot_helper._prepare_long_df(
                csv_files, valid_tags, x_col, y_cols, log
            )
            plot_helper._plot_with_plotly(
                df_long, valid_tags, outdir, save_fig, out_fmt, font_size, x_col, y_cols
            )

        if update_in_min > 0:
            interval = int(update_in_min * 60)
            console.log(f"Live update every {interval}s. Press Ctrl+C to stop.")
            try:
                while True:
                    run_once()
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.log("Stopped live updates.")
        else:
            run_once()
    @staticmethod
    def plot_image_grid(csv_path, sep=";", max_width=300, max_height=300):
        """
        Plot a grid of images using Plotly from a CSV file.

        Args:
            csv_path (str): Path to CSV file.
            max_width (int): Maximum width of each image in pixels.
            max_height (int): Maximum height of each image in pixels.
        """
        # Load CSV
        df = csvfile.read_auto_sep(csv_path, sep=sep)

        # Column names for headers
        col_names = df.columns.tolist()

        # Function to convert image to base64
        def pil_to_base64(img_path):
            with Image.open(img_path) as im:
                im.thumbnail((max_width, max_height))
                buffer = BytesIO()
                im.save(buffer, format="PNG")
                encoded = base64.b64encode(buffer.getvalue()).decode()
                return "data:image/png;base64," + encoded

        # Initialize figure
        fig = go.Figure()

        n_rows = len(df)
        n_cols = len(df.columns) - 1  # skip label column

        # Add images
        for i, row in df.iterrows():
            for j, col in enumerate(df.columns[1:]):
                img_path = row[col]
                img_src = pil_to_base64(img_path)
                fig.add_layout_image(
                    dict(
                        source=img_src,
                        x=j,
                        y=-i,  # negative to have row 0 on top
                        xref="x",
                        yref="y",
                        sizex=1,
                        sizey=1,
                        xanchor="left",
                        yanchor="top",
                        layer="above"
                    )
                )

        # Set axes for grid layout
        fig.update_xaxes(
            tickvals=list(range(n_cols)),
            ticktext=list(df.columns[1:]),
            range=[-0.5, n_cols-0.5],
            showgrid=False,
            zeroline=False
        )
        fig.update_yaxes(
            tickvals=[-i for i in range(n_rows)],
            ticktext=df[df.columns[0]],
            range=[-n_rows + 0.5, 0.5],
            showgrid=False,
            zeroline=False
        )

        fig.update_layout(
            width=max_width*n_cols,
            height=max_height*n_rows,
            margin=dict(l=100, r=20, t=50, b=50)
        )

        fig.show()

    @staticmethod
    # this plot_df contains the data to be plotted (row, column)
    def img_grid_df(input_dir, log=False):
        rows = fs.list_dirs(input_dir)
        rows = [r for r in rows if r.startswith("row")]
        meta_dict = {}
        cols_of_row = None
        for row in rows:
            row_path = os.path.join(input_dir, row)
            cols = sorted(fs.list_dirs(row_path))
            if cols_of_row is None:
                cols_of_row = cols
            else:
                if cols_of_row != cols:
                    raise ValueError(
                        f"Row {row} has different columns than previous rows: {cols_of_row} vs {cols}"
                    )
            meta_dict[row] = cols

        meta_dict_with_paths = {}
        for row, cols in meta_dict.items():
            meta_dict_with_paths[row] = {
                col: fs.filter_files_by_extension(
                    os.path.join(input_dir, row, col), ["png", "jpg", "jpeg"]
                )
                for col in cols
            }
        first_row = list(meta_dict_with_paths.keys())[0]
        first_col = list(meta_dict_with_paths[first_row].keys())[0]
        len_first_col = len(meta_dict_with_paths[first_row][first_col])
        for row, cols in meta_dict_with_paths.items():
            for col, paths in cols.items():
                if len(paths) != len_first_col:
                    raise ValueError(
                        f"Row {row}, Column {col} has different number of files: {len(paths)} vs {len_first_col}"
                    )
        cols = sorted(meta_dict_with_paths[first_row].keys())
        rows_set = sorted(meta_dict_with_paths.keys())
        row_per_col = len(meta_dict_with_paths[first_row][first_col])
        rows = [item for item in rows_set for _ in range(row_per_col)]
        data_dict = {}
        data_dict["row"] = rows
        col_data = {col: [] for col in cols}
        for row_base in rows_set:
            for col in cols:
                for i in range(row_per_col):
                    col_data[col].append(meta_dict_with_paths[row_base][col][i])
        data_dict.update(col_data)
        df = pd.DataFrame(data_dict)
        if log:
            csvfile.fn_display_df(df)
        return df

    @staticmethod
    def plot_image_grid(
        csv_file_or_df: Union[str, pd.DataFrame],
        max_width: int = 300,
        max_height: int = 300,
        img_stack_direction: str = "horizontal",
        img_stack_padding_px: int = 10,
        format_row_label_func: Optional[Callable[[str], str]] = None,
        format_col_label_func: Optional[Callable[[str, str], str]] = None,
        title: str = "",
    ):
        """
        Plot a grid of images using Plotly from a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame with first column as row labels, remaining columns as image paths.
            max_width (int): Maximum width of stacked images per cell in pixels.
            max_height (int): Maximum height of stacked images per cell in pixels.
            img_stack_direction (str): "horizontal" or "vertical" stacking.
            img_stack_padding_px (int): Padding between stacked images in pixels.
            format_row_label_func (Callable): Function to format row labels.
            format_col_label_func (Callable): Function to format column labels.
            title (str): Figure title.
        """

        def stack_images_base64(
            image_paths: List[str], direction: str, target_size: Tuple[int, int]
        ) -> str:
            """Stack images and return base64-encoded PNG."""
            if not image_paths:
                return ""

            processed_images = []
            for path in image_paths:
                try:
                    img = Image.open(path).convert("RGB")
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    processed_images.append(img)
                except:
                    # blank image if error
                    processed_images.append(Image.new("RGB", target_size, (255, 255, 255)))

            # Stack
            widths, heights = zip(*(img.size for img in processed_images))
            if direction == "horizontal":
                total_width = sum(widths) + img_stack_padding_px * (
                    len(processed_images) - 1
                )
                total_height = max(heights)
                stacked = Image.new("RGB", (total_width, total_height), (255, 255, 255))
                x_offset = 0
                for im in processed_images:
                    stacked.paste(im, (x_offset, 0))
                    x_offset += im.width + img_stack_padding_px
            elif direction == "vertical":
                total_width = max(widths)
                total_height = sum(heights) + img_stack_padding_px * (
                    len(processed_images) - 1
                )
                stacked = Image.new("RGB", (total_width, total_height), (255, 255, 255))
                y_offset = 0
                for im in processed_images:
                    stacked.paste(im, (0, y_offset))
                    y_offset += im.height + img_stack_padding_px
            else:
                raise ValueError("img_stack_direction must be 'horizontal' or 'vertical'")

            # Encode as base64
            buffer = BytesIO()
            stacked.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode()
            return "data:image/png;base64," + encoded

        # Load DataFrame if a file path is provided
        if isinstance(csv_file_or_df, str):
            df = csvfile.read_auto_sep(csv_file_or_df)
        else:
            df = csv_file_or_df
        assert isinstance(df, pd.DataFrame), "Input must be a DataFrame or valid CSV file path"

        rows = df[df.columns[0]].tolist()
        columns = df.columns[1:].tolist()
        n_rows, n_cols = len(rows), len(columns)

        fig = go.Figure()

        for i, row_label in enumerate(rows):
            for j, col_label in enumerate(columns):
                image_paths = df.loc[i, col_label]
                if isinstance(image_paths, str):
                    image_paths = [image_paths]
                img_src = stack_images_base64(
                    image_paths, img_stack_direction, (max_width, max_height)
                )

                fig.add_layout_image(
                    dict(
                        source=img_src,
                        x=j,
                        y=-i,  # negative so row 0 on top
                        xref="x",
                        yref="y",
                        sizex=1,
                        sizey=1,
                        xanchor="left",
                        yanchor="top",
                        layer="above",
                    )
                )

        # Format axis labels
        col_labels = [
            format_col_label_func(c, pattern="___") if format_col_label_func else c
            for c in columns
        ]
        row_labels = [
            format_row_label_func(r) if format_row_label_func else r for r in rows
        ]

        fig.update_xaxes(
            tickvals=list(range(n_cols)),
            ticktext=col_labels,
            range=[-0.5, n_cols - 0.5],
            showgrid=False,
            zeroline=False,
        )
        fig.update_yaxes(
            tickvals=[-i for i in range(n_rows)],
            ticktext=row_labels,
            range=[-n_rows + 0.5, 0.5],
            showgrid=False,
            zeroline=False,
        )

        fig.update_layout(
            width=max_width * n_cols + 200,  # extra for labels
            height=max_height * n_rows + 100,
            title=title,
            margin=dict(l=100, r=20, t=50, b=50),
        )

        fig.show()


@click.command()
@click.option("--csvfiles", "-f", multiple=True, type=str, help="csv files to plot")
@click.option(
    "--outdir", "-o", type=str, default=str(desktop_path), help="output directory"
)
@click.option(
    "--tags", "-t", multiple=True, type=str, default=[], help="tags for the csv files"
)
@click.option("--log", "-l", is_flag=True, help="log the csv files")
@click.option("--save_fig", "-s", is_flag=True, help="save the plot as file")
@click.option(
    "--update_in_min",
    "-u",
    type=float,
    default=0.0,
    help="update the plot every x minutes",
)
@click.option(
    "--x_col", "-x", type=str, default="epoch", help="column to use as x-axis"
)
@click.option(
    "--y_cols",
    "-y",
    multiple=True,
    type=str,
    required=True,
    help="columns to plot as y (can repeat)",
)
def main(csvfiles, outdir, tags, log, save_fig, update_in_min, x_col, y_cols):
    PlotHelper.plot_csv_timeseries(
        list(csvfiles),
        outdir,
        list(tags),
        log,
        save_fig,
        update_in_min,
        x_col=x_col,
        y_cols=list(y_cols),
    )


if __name__ == "__main__":
    main()
