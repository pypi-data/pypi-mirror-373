# This script create a test version
# of the watcam (wc) dataset
# for testing the tflite model

from argparse import ArgumentParser

from rich import inspect
from common import console, seed_everything, ConsoleLog
from sklearn.model_selection import StratifiedShuffleSplit, ShuffleSplit
from tqdm import tqdm
import os
import click
from torchvision.datasets import ImageFolder
import shutil
from rich.pretty import pprint
from system import filesys as fs
import glob


def parse_args():
    parser = ArgumentParser(description="desc text")
    parser.add_argument(
        "-indir",
        "--indir",
        type=str,
        help="orignal dataset path",
    )
    parser.add_argument(
        "-outdir",
        "--outdir",
        type=str,
        help="dataset out path",
        default=".",  # default to current dir
    )
    parser.add_argument(
        "-val_size",
        "--val_size",
        type=float,
        help="validation size",  # no default value to force user to input
        default=0.2,
    )
    # add using StratifiedShuffleSplit or ShuffleSplit
    parser.add_argument(
        "-seed",
        "--seed",
        type=int,
        help="random seed",
        default=42,
    )
    parser.add_argument(
        "-inplace",
        "--inplace",
        action="store_true",
        help="inplace operation, will overwrite the outdir if exists",
    )

    parser.add_argument(
        "-stratified",
        "--stratified",
        action="store_true",
        help="use StratifiedShuffleSplit instead of ShuffleSplit",
    )
    parser.add_argument(
        "-no_train",
        "--no_train",
        action="store_true",
        help="only create test set, no train set",
    )
    parser.add_argument(
        "-reverse",
        "--reverse",
        action="store_true",
        help="combine train and val set back to original dataset",
    )
    return parser.parse_args()


def move_images(image_paths, target_set_dir):
    for img_path in tqdm(image_paths):
        # get folder name of the image
        img_dir = os.path.dirname(img_path)
        out_cls_dir = os.path.join(target_set_dir, os.path.basename(img_dir))
        if not os.path.exists(out_cls_dir):
            os.makedirs(out_cls_dir)
        # move the image to the class folder
        shutil.move(img_path, out_cls_dir)


def split_dataset_cls(
    indir, outdir, val_size, seed, inplace, stratified_split, no_train
):
    seed_everything(seed)
    console.rule("Config confirm?")
    pprint(locals())
    click.confirm("Continue?", abort=True)
    assert os.path.exists(indir), f"{indir} does not exist"

    if not inplace:
        assert (not inplace) and (
            not os.path.exists(outdir)
        ), f"{outdir} already exists; SKIP ...."

    if inplace:
        outdir = indir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    console.rule(f"Creating train/val dataset")

    sss = (
        ShuffleSplit(n_splits=1, test_size=val_size)
        if not stratified_split
        else StratifiedShuffleSplit(n_splits=1, test_size=val_size)
    )

    pprint({"split strategy": sss, "indir": indir, "outdir": outdir})
    dataset = ImageFolder(
        root=indir,
        transform=None,
    )
    train_dataset_indices = None
    val_dataset_indices = None  # val here means test
    for train_indices, val_indices in sss.split(dataset.samples, dataset.targets):
        train_dataset_indices = train_indices
        val_dataset_indices = val_indices

    # get image paths for train/val split dataset
    train_image_paths = [dataset.imgs[i][0] for i in train_dataset_indices]
    val_image_paths = [dataset.imgs[i][0] for i in val_dataset_indices]

    # start creating train/val folders then move images
    out_train_dir = os.path.join(outdir, "train")
    out_val_dir = os.path.join(outdir, "val")
    if inplace:
        assert os.path.exists(out_train_dir) == False, f"{out_train_dir} already exists"
        assert os.path.exists(out_val_dir) == False, f"{out_val_dir} already exists"

    os.makedirs(out_train_dir)
    os.makedirs(out_val_dir)

    if not no_train:
        with ConsoleLog(f"Moving train images to {out_train_dir} "):
            move_images(train_image_paths, out_train_dir)
    else:
        pprint("test only, skip moving train images")
        # remove out_train_dir
        shutil.rmtree(out_train_dir)

    with ConsoleLog(f"Moving val images to {out_val_dir} "):
        move_images(val_image_paths, out_val_dir)

    if inplace:
        pprint(f"remove all folders, except train and val")
        for cls_dir in os.listdir(outdir):
            if cls_dir not in ["train", "val"]:
                shutil.rmtree(os.path.join(indir, cls_dir))


def reverse_split_ds(indir):
    console.rule(f"Reversing split dataset <{indir}>...")
    ls_dirs = os.listdir(indir)
    # make sure there are only two dirs 'train' and 'val'
    assert len(ls_dirs) == 2, f"Found more than 2 dirs: {len(ls_dirs) } dirs"
    assert "train" in ls_dirs, f"train dir not found in {indir}"
    assert "val" in ls_dirs, f"val dir not found in {indir}"
    train_dir = os.path.join(indir, "train")
    val_dir = os.path.join(indir, "val")
    all_train_files = fs.filter_files_by_extension(
        train_dir, ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]
    )
    all_val_files = fs.filter_files_by_extension(
        val_dir, ["jpg", "jpeg", "png", "bmp", "gif", "tiff"]
    )
    # move all files from train to indir
    with ConsoleLog(f"Moving train images to {indir} "):
        move_images(all_train_files, indir)
    with ConsoleLog(f"Moving val images to {indir} "):
        move_images(all_val_files, indir)
    with ConsoleLog(f"Removing train and val dirs"):
        # remove train and val dirs
        shutil.rmtree(train_dir)
        shutil.rmtree(val_dir)


def main():
    args = parse_args()
    indir = args.indir
    outdir = args.outdir
    if outdir == ".":
        # get current folder of the indir
        indir_parent_dir = os.path.dirname(os.path.normpath(indir))
        indir_name = os.path.basename(indir)
        outdir = os.path.join(indir_parent_dir, f"{indir_name}_split")
    val_size = args.val_size
    seed = args.seed
    inplace = args.inplace
    stratified_split = args.stratified
    no_train = args.no_train
    reverse = args.reverse
    if not reverse:
        split_dataset_cls(
            indir, outdir, val_size, seed, inplace, stratified_split, no_train
        )
    else:
        reverse_split_ds(indir)


if __name__ == "__main__":
    main()
