import pandas as pd
from rich.pretty import pprint
from argparse import ArgumentParser

def cols_to_col_groups(df):
    columns = list(df.columns)
    # pprint(columns)

    col_groups = []
    current_group = []

    def have_unnamed(col_group):
        return any("unnamed" in col.lower() for col in col_group)

    for i, col in enumerate(columns):
        # Add the first column to the current group
        if not current_group:
            current_group.append(col)
            continue

        prev_col = columns[i - 1]
        # Check if current column is "unnamed" or shares base name with previous
        # Assuming "equal" means same base name (before any suffix like '_1')
        base_prev = (
            prev_col.split("_")[0].lower() if "_" in prev_col else prev_col.lower()
        )
        base_col = col.split("_")[0].lower() if "_" in col else col.lower()
        is_unnamed = "unnamed" in col.lower()
        is_equal = base_col == base_prev

        if is_unnamed or is_equal:
            # Add to current group
            current_group.append(col)
        else:
            # Start a new group
            col_groups.append(current_group)
            current_group = [col]
    # Append the last group
    if current_group:
        col_groups.append(current_group)
    meta_dict = {"common_cols": [], "db_cols": []}
    for group in col_groups:
        if not have_unnamed(group):
            meta_dict["common_cols"].extend(group)
        else:
            # find the first unnamed column
            named_col = next(
                (col for col in group if "unnamed" not in col.lower()), None
            )
            group_cols = [f"{named_col}_{i}" for i in range(len(group))]
            meta_dict["db_cols"].extend(group_cols)
    return meta_dict

# def bech_by_db_name(df, db_list="db1, db2", key_metrics="p, r, f1, acc"):


def str_2_list(input_str, sep=","):
    out_ls = []
    if len(input_str.strip()) == 0:
        return out_ls
    if sep not in input_str:
        out_ls.append(input_str.strip())
        return out_ls
    else:
        out_ls = [item.strip() for item in input_str.split(sep) if item.strip()]
        return out_ls


def filter_bech_df_by_db_and_metrics(df, db_list="", key_metrics=""):
    meta_cols_dict = cols_to_col_groups(df)
    op_df = df.copy()
    op_df.columns = (
        meta_cols_dict["common_cols"].copy() + meta_cols_dict["db_cols"].copy()
    )
    filterd_cols = []
    filterd_cols.extend(meta_cols_dict["common_cols"])

    selected_db_list = str_2_list(db_list)
    db_filted_cols = []
    if len(selected_db_list) > 0:
        for db_name in db_list.split(","):
            db_name = db_name.strip()
            for col_name in meta_cols_dict["db_cols"]:
                if db_name.lower() in col_name.lower():
                    db_filted_cols.append(col_name)
    else:
        db_filted_cols = meta_cols_dict["db_cols"]

    filterd_cols.extend(db_filted_cols)
    df_filtered = op_df[filterd_cols].copy()
    df_filtered

    selected_metrics_ls = str_2_list(key_metrics)
    if len(selected_metrics_ls) > 0:
        # get the second row as metrics row (header)
        metrics_row = df_filtered.iloc[0].copy()
        # only get the values in columns in (db_filterd_cols)
        metrics_values = metrics_row[db_filted_cols].values
        keep_metrics_cols = []
        # create a zip of db_filted_cols and metrics_values (in that metrics_row)
        metrics_list = list(zip(metrics_values, db_filted_cols))
        selected_metrics_ls = [metric.strip().lower() for metric in selected_metrics_ls]
        for metric, col_name in metrics_list:
            if metric.lower() in selected_metrics_ls:
                keep_metrics_cols.append(col_name)

    else:
        pprint("No metrics selected, keeping all db columns")
        keep_metrics_cols = db_filted_cols

    final_filterd_cols = meta_cols_dict["common_cols"].copy() + keep_metrics_cols
    df_final = df_filtered[final_filterd_cols].copy()
    return df_final


def parse_args():
    parser = ArgumentParser(
        description="desc text")
    parser.add_argument('-csv', '--csv', type=str, help='CSV file path', default=r"E:\Dev\__halib\test\bench.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    csv_file = args.csv
    df = pd.read_csv(csv_file, sep=";", encoding="utf-8")
    filtered_df = filter_bech_df_by_db_and_metrics(df, "bowfire", "acc")
    print(filtered_df)

if __name__ == "__main__":
    main()
