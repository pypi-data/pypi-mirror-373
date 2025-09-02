"""
 * @author Hoang Van-Ha
 * @email hoangvanhauit@gmail.com
 * @create date 2024-03-27 15:40:22
 * @modify date 2024-03-27 15:40:22
 * @desc this module works as a utility tools for finding the best configuration for dataloader (num_workers, batch_size, pin_menory, etc.) that fits your hardware.
"""
from argparse import ArgumentParser
from .common import *
from .filetype import csvfile
from .filetype.yamlfile import load_yaml
from rich import inspect
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm
from typing import Union
import itertools as it  # for cartesian product
import os
import time
import traceback


def parse_args():
    parser = ArgumentParser(description="desc text")
    parser.add_argument("-cfg", "--cfg", type=str, help="cfg file for searching")
    return parser.parse_args()


def get_test_range(cfg: dict, search_item="num_workers"):
    item_search_cfg = cfg["search_space"].get(search_item, None)
    if item_search_cfg is None:
        raise ValueError(f"search_item: {search_item} not found in cfg")
    if isinstance(item_search_cfg, list):
        return item_search_cfg
    elif isinstance(item_search_cfg, dict):
        if "mode" in item_search_cfg:
            mode = item_search_cfg["mode"]
            assert mode in ["range", "list"], f"mode: {mode} not supported"
            value_in_mode = item_search_cfg.get(mode, None)
            if value_in_mode is None:
                raise ValueError(f"mode<{mode}>: data not found in <{search_item}>")
            if mode == "range":
                assert len(value_in_mode) == 3, f"range must have 3 values: start, stop, step"
                start = value_in_mode[0]
                stop = value_in_mode[1]
                step = value_in_mode[2]
                return list(range(start, stop, step))
            elif mode == "list":
                return item_search_cfg["list"]
    else:
        return [item_search_cfg]  # for int, float, str, bool, etc.


def load_an_batch(loader_iter):
    start = time.time()
    next(loader_iter)
    end = time.time()
    return end - start


def test_dataloader_with_cfg(origin_dataloader: DataLoader, cfg: Union[dict, str]):
    try:
        if isinstance(cfg, str):
            cfg = load_yaml(cfg, to_dict=True)
        dfmk = csvfile.DFCreator()
        search_items = ["batch_size", "num_workers", "persistent_workers", "pin_memory"]
        batch_limit = cfg["general"]["batch_limit"]
        csv_cfg = cfg["general"]["to_csv"]
        log_batch_info = cfg["general"]["log_batch_info"]

        save_to_csv = csv_cfg["enabled"]
        log_dir = csv_cfg["log_dir"]
        filename = csv_cfg["filename"]
        filename = f"{now_str()}_{filename}.csv"
        outfile = os.path.join(log_dir, filename)

        dfmk.create_table(
            "cfg_search",
            (search_items + ["avg_time_taken"]),
        )
        ls_range_test = []
        for item in search_items:
            range_test = get_test_range(cfg, search_item=item)
            range_test = [(item, i) for i in range_test]
            ls_range_test.append(range_test)

        all_combinations = list(it.product(*ls_range_test))

        rows = []
        for cfg_idx, combine in enumerate(all_combinations):
            console.rule(f"Testing cfg {cfg_idx+1}/{len(all_combinations)}")
            inspect(combine)
            batch_size = combine[search_items.index("batch_size")][1]
            num_workers = combine[search_items.index("num_workers")][1]
            persistent_workers = combine[search_items.index("persistent_workers")][1]
            pin_memory = combine[search_items.index("pin_memory")][1]

            test_dataloader = DataLoader(origin_dataloader.dataset, batch_size=batch_size, num_workers=num_workers, persistent_workers=persistent_workers, pin_memory=pin_memory, shuffle=True)
            row = [
                batch_size,
                num_workers,
                persistent_workers,
                pin_memory,
                0.0,
            ]

            # calculate the avg time taken to load the data for <batch_limit> batches
            trainiter = iter(test_dataloader)
            time_elapsed = 0
            pprint('Start testing...')
            for i in tqdm(range(batch_limit)):
                single_batch_time = load_an_batch(trainiter)
                if log_batch_info:
                    pprint(f"Batch {i+1} took {single_batch_time:.4f} seconds to load")
                time_elapsed += single_batch_time
            row[-1] = time_elapsed / batch_limit
            rows.append(row)
        dfmk.insert_rows('cfg_search', rows)
        dfmk.fill_table_from_row_pool('cfg_search')
        with ConsoleLog("results"):
            csvfile.fn_display_df(dfmk['cfg_search'])
            if save_to_csv:
                dfmk["cfg_search"].to_csv(outfile, index=False)
                console.print(f"[red] Data saved to <{outfile}> [/red]")

    except Exception as e:
        traceback.print_exc()
        print(e)
        # get current directory of this python file
        current_dir = os.path.dirname(os.path.realpath(__file__))
        standar_cfg_path = os.path.join(current_dir, "torchloader_search.yaml")
        pprint(
            f"Make sure you get the  right <cfg.yaml> file. An example of <cfg.yaml> file can be found at this path: {standar_cfg_path}"
        )
        return

def main():
    args = parse_args()
    cfg_yaml = args.cfg
    cfg_dict = load_yaml(cfg_yaml, to_dict=True)

    # Define transforms for data augmentation and normalization
    transform = transforms.Compose(
        [
            transforms.RandomHorizontalFlip(),  # Randomly flip images horizontally
            transforms.RandomRotation(10),  # Randomly rotate images by 10 degrees
            transforms.ToTensor(),  # Convert images to PyTorch tensors
            transforms.Normalize(
                (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)
            ),  # Normalize pixel values to [-1, 1]
        ]
    )
    test_dataset = datasets.CIFAR10(
        root="./data", train=False, download=True, transform=transform
    )
    batch_size = 64
    train_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)
    test_dataloader_with_cfg(train_loader, cfg_dict)


if __name__ == "__main__":
    main()
