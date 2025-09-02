# -*- coding: utf-8 -*-

"""
    Upload folder to Google Drive
"""
import ast
import os

import googleapiclient.errors
# Import Google libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFileList

from halib.system import filesys
from halib.filetype import textfile

# Import general libraries

ggDrive = None


def get_gg_drive(settings_file='settings.yaml'):
    """
        Authenticate to Google API
    """
    global ggDrive
    if ggDrive is None:
        ggAuth = GoogleAuth(settings_file=settings_file)
        ggDrive = GoogleDrive(ggAuth)
    return ggDrive


def get_folder_id(gg_parent_folder_id, folder_name):
    """
    Check if destination folder exists and return it's ID
    """

    # Auto-iterate through all files in the parent folder.
    drive = get_gg_drive()
    file_list = GoogleDriveFileList()
    try:
        file_list = drive.ListFile(
            {'q': "'{0}' in parents and trashed=false".format(gg_parent_folder_id)}
        ).GetList()
    # Exit if the parent folder doesn't exist
    except googleapiclient.errors.HttpError as err:
        # Parse error message
        message = ast.literal_eval(err.content)['error']['message']
        if message == 'File not found: ':
            print(message + folder_name)
            exit(1)
        # Exit with stacktrace in case of other error
        else:
            raise

    # Find the the destination folder in the parent folder's files
    for file1 in file_list:
        if file1['title'] == folder_name:
            print('title: %s, id: %s' % (file1['title'], file1['id']))
            return file1['id']


def create_folder(folder_name, gg_parent_folder_id):
    """
        Create folder on Google Drive
    """

    folder_metadata = {
        'title': folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
        # ID of the parent folder
        'parents': [{"kind": "drive#fileLink", "id": gg_parent_folder_id}]
    }
    drive = get_gg_drive()
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Return folder information
    # print('title: %s, id: %s' % (folder['title'], folder['id']))
    return folder['id']


def is_in_ignore_list(local_path, ignore_list=None):
    in_ignore_list = False
    if ignore_list:
        for path in ignore_list:
            if path in local_path:
                in_ignore_list = True
                break
    return in_ignore_list


def upload_file(local_file_path, gg_folder_id, ignore_list=None):
    """
        Upload local file to Google Drive folder
    """
    drive = get_gg_drive()
    if not is_in_ignore_list(local_file_path, ignore_list):
        print('uploading ' + local_file_path)
        # Upload file to folder.
        title = filesys.get_file_name(local_file_path, split_file_ext=False)

        # delete file if exist on gg folder
        query = f"'{gg_folder_id}'  in parents and trashed=false"
        file_list = drive.ListFile({'q': f"{query}"}).GetList()
        for file in file_list:
            if file['title'] == title:
                print(f'[DELETE] {title} on Google Drive')
                file.Delete()
                break

        f = drive.CreateFile(
            {"title": f"{title}",
             "parents": [{"kind": "drive#fileLink", "id": gg_folder_id}]})
        f.SetContentFile(local_file_path)
        f.Upload()
    # Skip the file if it's empty
    else:
        print('file {0} is empty or in ignore list'.format(local_file_path))


def recursive_walk_and_upload(local_folder_path, gg_folder_id,
                              processed_path, ignore_list=None):
    for root, sub_folders, files in os.walk(local_folder_path):
        # already processed folder
        if root in processed_path:
            print(f'[SKIP] already processed folder {root}')
            return
        print(f'\n\n[RECURSIVE] {local_folder_path}, {gg_folder_id}')
        print(f'[FF] {root} {sub_folders} {files}')
        if sub_folders:
            for sub_folder in sub_folders:
                sub_folder_path = os.path.join(root, sub_folder)
                print(f'process {sub_folder_path}')
                if is_in_ignore_list(sub_folder_path, ignore_list):
                    continue
                # Get destination folder ID
                gg_sub_folder_id = get_folder_id(gg_folder_id, sub_folder)
                # Create the folder if it doesn't exists
                if not gg_sub_folder_id:
                    print('creating folder ' + sub_folder)
                    gg_sub_folder_id = create_folder(sub_folder, gg_folder_id)
                recursive_walk_and_upload(sub_folder_path, gg_sub_folder_id,
                                          processed_path, ignore_list)
        if files:
            for file in files:
                filePath = os.path.join(root, file)
                upload_file(filePath, gg_folder_id, ignore_list)
        processed_path.append(root)


def upload_folder_to_drive(local_folder, gg_folder_id,
                           content_only=True,
                           ignore_file=None):
    """
       Upload folder to Google Drive folder
       bool content_only: if true, we only upload files and folder inside local_folder
       else create a folder with the same name of the local folder and upload all files and folders
       in the local folder to it
   """

    ignore_list = None
    if ignore_file:
        if filesys.is_file(ignore_file):
            ignore_list = textfile.read_line_by_line(ignore_file)
            ignore_list = [os.path.normpath(path) for path in ignore_list]

    if content_only is False:
        folder_name = filesys.get_dir_name(local_folder)
        gg_folder_id_to_upload = create_folder(folder_name, gg_folder_id)
    else:
        gg_folder_id_to_upload = gg_folder_id

    processed_path = []
    local_folder = os.path.normpath(local_folder)
    recursive_walk_and_upload(local_folder, gg_folder_id_to_upload,
                              processed_path, ignore_list)
