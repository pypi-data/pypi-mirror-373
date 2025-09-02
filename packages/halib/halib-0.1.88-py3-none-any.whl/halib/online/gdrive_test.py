from argparse import ArgumentParser
import gdrive


def parse_args():
    parser = ArgumentParser(description="Upload local folder to Google Drive")
    parser.add_argument(
        "-a",
        "--authFile",
        type=str,
        help="authenticate file to Google Drive",
        default="settings.yaml",
    )
    parser.add_argument("-s", "--source", type=str, help="Folder to upload")
    parser.add_argument(
        "-d", "--destination", type=str, help="Destination folder ID in Google Drive"
    )
    parser.add_argument(
        "-c",
        "--contentOnly",
        type=str,
        help="Parent Folder in Google Drive",
        default="True",
    )
    parser.add_argument(
        "-i",
        "--ignoreFile",
        type=str,
        help="file containing files/folders to ignore",
        default=None,
    )

    return parser.parse_args()


def main():
    args = parse_args()
    auth_file = args.authFile
    local_folder = args.source
    gg_folder_id = args.destination
    content_only = args.contentOnly.lower() == "true"
    ignore_file = args.ignoreFile
    gdrive.get_gg_drive(auth_file)
    gdrive.upload_folder_to_drive(
        local_folder, gg_folder_id, content_only=content_only, ignore_file=ignore_file
    )


if __name__ == "__main__":
    main()
