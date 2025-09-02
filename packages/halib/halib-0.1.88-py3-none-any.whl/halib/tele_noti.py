# Watch a log file and send a telegram message when train reaches a certain epoch or end

import os
import yaml
import asyncio
import telegram
import pandas as pd

from rich.pretty import pprint
from rich.console import Console
import plotly.graph_objects as go

from .system import filesys as fs
from .filetype import textfile, csvfile

from argparse import ArgumentParser

tele_console = Console()


def parse_args():
    parser = ArgumentParser(description="desc text")
    parser.add_argument(
        "-cfg",
        "--cfg",
        type=str,
        help="yaml file for tele",
        default=r"E:\Dev\halib\cfg_tele_noti.yaml",
    )

    return parser.parse_args()


def get_watcher_message_df(target_file, num_last_lines):
    file_ext = fs.get_file_name(target_file, split_file_ext=True)[1]
    supported_ext = [".txt", ".log", ".csv"]
    assert (
        file_ext in supported_ext
    ), f"File extension {file_ext} not supported. Supported extensions are {supported_ext}"
    last_lines_df = None
    if file_ext in [".txt", ".log"]:
        lines = textfile.read_line_by_line(target_file)
        if num_last_lines > len(lines):
            num_last_lines = len(lines)
        last_line_arr = lines[-num_last_lines:]
        # add a line start with word "epoch"
        epoch_info_list = "Epoch: n/a"
        for line in reversed(lines):
            if "epoch" in line.lower():
                epoch_info_list = line
                break
        last_line_arr.insert(0, epoch_info_list)  # insert at the beginning
        dfCreator = csvfile.DFCreator()
        dfCreator.create_table("last_lines", ["line"])
        last_line_arr = [[line] for line in last_line_arr]
        dfCreator.insert_rows("last_lines", last_line_arr)
        dfCreator.fill_table_from_row_pool("last_lines")
        last_lines_df = dfCreator["last_lines"].copy()
    else:
        df = pd.read_csv(target_file)
        num_rows = len(df)
        if num_last_lines > num_rows:
            num_last_lines = num_rows
        last_lines_df = df.tail(num_last_lines)
    return last_lines_df


def df2img(df: pd.DataFrame, output_img_dir, decimal_places, out_img_scale):
    df = df.round(decimal_places)
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=list(df.columns), align="center"),
                cells=dict(
                    values=df.values.transpose(),
                    fill_color=[["white", "lightgrey"] * df.shape[0]],
                    align="center",
                ),
            )
        ]
    )
    if not os.path.exists(output_img_dir):
        os.makedirs(output_img_dir)
    img_path = os.path.normpath(os.path.join(output_img_dir, "last_lines.png"))
    fig.write_image(img_path, scale=out_img_scale)
    return img_path


def compose_message_and_img_path(
    target_file, project, num_last_lines, decimal_places, out_img_scale, output_img_dir
):
    context_msg = f">> Project: {project} \n>> File: {target_file} \n>> Last {num_last_lines} lines:"
    msg_df = get_watcher_message_df(target_file, num_last_lines)
    try:
        img_path = df2img(msg_df, output_img_dir, decimal_places, out_img_scale)
    except Exception as e:
        pprint(f"Error: {e}")
        img_path = None
    return context_msg, img_path


async def send_to_telegram(cfg_dict, interval_in_sec):
    # pprint(cfg_dict)
    token = cfg_dict["telegram"]["token"]
    chat_id = cfg_dict["telegram"]["chat_id"]

    noti_settings = cfg_dict["noti_settings"]
    project = noti_settings["project"]
    target_file = noti_settings["target_file"]
    num_last_lines = noti_settings["num_last_lines"]
    output_img_dir = noti_settings["output_img_dir"]
    decimal_places = noti_settings["decimal_places"]
    out_img_scale = noti_settings["out_img_scale"]

    bot = telegram.Bot(token=token)
    async with bot:
        try:
            context_msg, img_path = compose_message_and_img_path(
                target_file,
                project,
                num_last_lines,
                decimal_places,
                out_img_scale,
                output_img_dir,
            )
            time_now = next_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            sep_line = "-" * 50
            context_msg = f"{sep_line}\n>> Time: {time_now}\n{context_msg}"
            # calculate the next time to send message
            next_time = pd.Timestamp.now() + pd.Timedelta(seconds=interval_in_sec)
            next_time = next_time.strftime("%Y-%m-%d %H:%M:%S")
            next_time_info = f"Next msg: {next_time}"
            tele_console.rule()
            tele_console.print("[green] Send message to telegram [/green]")
            tele_console.print(
                f"[red] Next message will be sent at <{next_time}> [/red]"
            )
            await bot.send_message(text=context_msg, chat_id=chat_id)
            if img_path:
                await bot.send_photo(chat_id=chat_id, photo=open(img_path, "rb"))
            await bot.send_message(text=next_time_info, chat_id=chat_id)
        except Exception as e:
            pprint(f"Error: {e}")
            pprint("Message not sent to telegram")


async def run_forever(cfg_path):
    cfg_dict = yaml.safe_load(open(cfg_path, "r"))
    noti_settings = cfg_dict["noti_settings"]
    interval_in_min = noti_settings["interval_in_min"]
    interval_in_sec = int(interval_in_min * 60)
    pprint(
        f"Message will be sent every {interval_in_min} minutes or {interval_in_sec} seconds"
    )
    while True:
        await send_to_telegram(cfg_dict, interval_in_sec)
        await asyncio.sleep(interval_in_sec)


async def main():
    args = parse_args()
    await run_forever(args.cfg)


if __name__ == "__main__":
    asyncio.run(main())
