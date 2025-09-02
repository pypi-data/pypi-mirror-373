import pandas as pd
from tabulate import tabulate
from rich.console import Console
from rich import print as rprint
from rich import inspect
from rich.pretty import pprint
from tqdm import tqdm
from loguru import logger
from itables import init_notebook_mode, show
import pygwalker as pyg
import textwrap
import csv

console = Console()


def read(file, separator=","):
    df = pd.read_csv(file, separator)
    return df


def read_auto_sep(filepath, sample_size=2048, **kwargs):
    """
    Read a CSV file with automatic delimiter detection.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    sample_size : int, optional
        Number of bytes to read for delimiter sniffing.
    **kwargs : dict
        Extra keyword args passed to pandas.read_csv.

    Returns
    -------
    df : pandas.DataFrame
    """
    with open(filepath, "r", newline="", encoding=kwargs.get("encoding", "utf-8")) as f:
        sample = f.read(sample_size)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|", ":"])
            sep = dialect.delimiter
        except csv.Error:
            sep = ","  # fallback if detection fails

    return pd.read_csv(filepath, sep=sep, **kwargs)

# for append, mode = 'a'
def fn_write(df, outfile, mode="w", header=True, index_label=None):
    if not outfile.endswith(".csv"):
        outfile = f"{outfile}.csv"
    if index_label is not None:
        df.to_csv(outfile, mode=mode, header=header, index_label=index_label)
    else:
        df.to_csv(outfile, mode=mode, header=header, index=False)


def fn_make_df_with_columns(columns):
    df = pd.DataFrame(columns=columns)
    return df


def fn_insert_rows(df, singleRow_or_rowList):
    row_data = (
        singleRow_or_rowList
        if type(singleRow_or_rowList[0]) is list
        else [singleRow_or_rowList]
    )
    new_row_df = pd.DataFrame(row_data, columns=df.columns)
    df = pd.concat([df, new_row_df], ignore_index=True)
    return df

    # Auto-wrap function for each cell
def auto_wrap(cell, width=40):
    return textwrap.fill(str(cell), width=width)

def fn_display_df(df, max_col_width=40):
    # Apply wrapping; tablefmt="psql" for PostgreSQL-like output
    # wrapped_df = df.applymap(lambda x: auto_wrap(x, width=max_col_width))
    # fix the future warning of applymap
    wrapped_df = df.apply(
        lambda col: col.map(lambda x: auto_wrap(x, width=max_col_width))
    )
    print(tabulate(wrapped_df, headers="keys", tablefmt="grid", numalign="right"))

def showdf(df, display_mode="itable", in_jupyter=True, all_interactive=False):
    if display_mode == "itable":
        if in_jupyter:
            init_notebook_mode(all_interactive=all_interactive)
        show(
            df,
            # layout={"top1": "searchPanes"},
            # searchPanes={"layout": "column-3", "cascadePanes": True},
            caption="table caption",
            layout={"top1": "searchBuilder"},
            buttons=["csvHtml5", "excelHtml5", "colvis"],
            search={"regex": True, "caseInsensitive": True},
            paging=False,  # no paging
            scrollY="300px",  # height of table
            scrollCollapse=True,
            showIndex=True,  # show row no.
            select=True,  # allow row selected
            keys=True,  # enable navigate using arrow keys
        )
    elif display_mode == "pygwalker":
        return pyg.walk(df)
    else:
        raise ValueError("Invalid display mode, current support [itable, pygwalker]")


def fn_config_display_pd(
    max_rows=None,
    max_columns=None,
    display_width=1000,
    col_header_justify="center",
    precision=10,
):
    pd.set_option("display.max_rows", max_rows)
    pd.set_option("display.max_columns", max_columns)
    pd.set_option("display.width", display_width)
    pd.set_option("display.colheader_justify", col_header_justify)
    pd.set_option("display.precision", precision)


class DFCreator(dict):
    """docstring for ClassName."""

    def __init__(self, *arg, **kw):
        super(DFCreator, self).__init__(*arg, **kw)
        self.row_pool_dict = {}

    def create_table(self, table_name, columns):
        self[table_name] = pd.DataFrame(columns=columns)
        self.row_pool_dict[table_name] = []

    """Instead of inserting to dataframe, insert to row pool for fast computation"""

    def insert_rows(self, table_name, singleRow_or_rowList):
        rows_data = (
            singleRow_or_rowList
            if type(singleRow_or_rowList[0]) is list
            else [singleRow_or_rowList]
        )
        self.row_pool_dict[table_name].extend(rows_data)

    """Fill from row pool to actual table dataframe"""

    def fill_table_from_row_pool(self, table_name):
        if len(self.row_pool_dict[table_name]) > 0:
            # concat row pool to table dataframe
            self[table_name] = fn_insert_rows(
                self[table_name], self.row_pool_dict[table_name]
            )
            # free the pool
            self.row_pool_dict[table_name] = []

    def write_table(
        self,
        table_name,
        output_dir,
        out_file_name=None,
        mode="w",
        header=True,
        index_label=None,
    ):
        self.fill_table_from_row_pool(table_name)

        if not out_file_name:
            outfile = f"{output_dir}/{table_name}.csv"
        else:
            outfile = f"{output_dir}/{out_file_name}.csv"

        fn_write(self[table_name], outfile, mode, header, index_label)

    def write_all_table(self, output_dir, mode="w", header=True, index_label=None):
        for table_name in self.keys():
            outfile = f"{output_dir}/{table_name}.csv"
            fn_write(self[table_name], outfile, mode, header, index_label)

    def display_table(self, table_name):
        self.fill_table_from_row_pool(table_name)
        fn_display_df(self[table_name])

    def display_table_schema(self, table_name):
        columns = list(self[table_name].columns)
        console.print(f"TABLE {table_name}: {columns}", style="bold blue")

    def display_all_table_schema(self):
        table_names = list(self.keys())
        for table_name in table_names:
            self.display_table_schema(table_name)

    def display_all_table(self):
        for table_name in self.keys():
            console.rule(table_name)
            self.display_table(table_name)
