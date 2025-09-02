from argparse import ArgumentParser
from datetime import datetime

import gdrive
from ..filetype import textfile


def parse_args():
    parser = ArgumentParser(description="Upload local folder to Google Drive")
    parser.add_argument(
        "-a",
        "--authFile",
        type=str,
        help="authenticate file to Google Drive",
        default="settings.yaml",
    )
    parser.add_argument(
        "-g",
        "--GDriveParentFolder",
        type=str,
        help="Destination parent folder ID in Google Drive",
    )
    parser.add_argument(
        "-n",
        "--folderName",
        type=str,
        help="name of the folder which is about to be created",
        default="untitled",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    auth_file = args.authFile
    gDrive_parent_folder_id = args.GDriveParentFolder
    folder_name = args.folderName

    if folder_name == "untitled":
        folder_name = datetime.today().strftime("%Y.%m.%d_%Hh%M")
    else:
        date_str = datetime.today().strftime("%Y.%m.%d_%Hh%M")
        folder_name = f"{date_str}_{folder_name}"

    print(f"[GDrive] creating {folder_name} in GDrive folder {gDrive_parent_folder_id}")

    gdrive.get_gg_drive(auth_file)
    folder_id = gdrive.create_folder(folder_name, gDrive_parent_folder_id)
    textfile.write([folder_id], "./GDriveFolder.txt")


if __name__ == "__main__":
    main()
