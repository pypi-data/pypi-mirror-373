import pandas as pd
from tabulate import tabulate


def read(file, separator=","):
    df = pd.read_csv(file, separator)
    return df


# for append, mode = 'a'
def write(df, outfile, mode='w', header=True, index_label=None):
    if not outfile.endswith('.csv'):
        outfile = f'{outfile}.csv'
    if index_label is not None:
        df.to_csv(outfile, mode=mode, header=header, index_label=index_label)
    else:
        df.to_csv(outfile, mode=mode, header=header, index=False)


def make_df_with_columns(columns):
    df = pd.DataFrame(columns=columns)
    return df


def insert_row(df, row_dict_or_list):
    if isinstance(row_dict_or_list, list):
        new_row_df = pd.DataFrame([row_dict_or_list], columns=df.columns)
        df = pd.concat([df, new_row_df], ignore_index=True)
        return df
    elif isinstance(row_dict_or_list, dict):
        df = df.append(row_dict_or_list, ignore_index=True)
        return df
    else:
        raise ValueError('invalid row data')


def display_df(df):
    print(tabulate(df, headers='keys', tablefmt='psql', numalign="right"))


def config_display_pd(max_rows=None, max_columns=None,
                      display_width=1000, col_header_justify='center',
                      precision=10):
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.width', display_width)
    pd.set_option('display.colheader_justify', col_header_justify)
    pd.set_option('display.precision', precision)
