# coding=utf-8
import json
import os
import shutil
from argparse import ArgumentParser
from io import BytesIO
import subprocess

import certifi
import pycurl
from ..filetype import jsonfile
from ..system import filesys


def get_curl(url, user_and_pass, verbose=True):
    c = pycurl.Curl()
    c.setopt(pycurl.VERBOSE, verbose)
    c.setopt(pycurl.CAINFO, certifi.where())
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.USERPWD, user_and_pass)
    return c


def get_user_and_pass(username, appPass):
    return f"{username}:{appPass}"


def create_repo(
    username, appPass, repo_name, workspace, proj_name, template_repo="py-proj-template"
):
    buffer = BytesIO()
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_name}"
    data = json.dumps({"scm": "git", "project": {"key": f"{proj_name}"}})

    user_and_pass = get_user_and_pass(username, appPass)
    c = get_curl(url, user_and_pass)
    c.setopt(pycurl.WRITEDATA, buffer)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    c.setopt(pycurl.HTTPHEADER, ["Accept: application/json"])
    c.perform()
    RESPOND_CODE = c.getinfo(pycurl.HTTP_CODE)
    c.close()
    # log info
    body = buffer.getvalue()
    msg = body.decode("iso-8859-1")
    successful = True if str(RESPOND_CODE) == "200" else False

    if successful and template_repo:
        template_repo_url = f"https://{username}:{appPass}@bitbucket.org/{workspace}/{template_repo}.git"
        git_clone(template_repo_url)
        template_folder = f"./{template_repo}"

        created_repo_url = (
            f"https://{username}:{appPass}@bitbucket.org/{workspace}/{repo_name}.git"
        )
        git_clone(created_repo_url)
        created_folder = f"./{repo_name}"
        shutil.copytree(
            template_folder,
            created_folder,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git"),
        )
        os.system('rmdir /S /Q "{}"'.format(template_folder))
        project_folder = "project_name"

        filesys.change_current_dir(created_folder)
        filesys.rename_dir_or_file(project_folder, repo_name)
        # push to remote
        subprocess.check_call(["C:/batch/gitp.bat", "init proj from template"])

    return successful, msg


def parse_args():
    parser = ArgumentParser(description="Upload local folder to Google Drive")
    parser.add_argument(
        "-a",
        "--authFile",
        type=str,
        help="authenticate file (json) to Bitbucket",
        default="bitbucket.json",
    )
    parser.add_argument(
        "-r", "--repoName", type=str, help="Repository name", default="hahv-proj"
    )
    parser.add_argument(
        "-t", "--templateRepo", type=str, help="template repo to fork", default="True"
    )
    return parser.parse_args()


def git_clone(url):
    subprocess.check_call(["git", "clone", url])


def main():
    args = parse_args()
    authFile = args.authFile
    repo_name = args.repoName

    authInfo = jsonfile.read(authFile)
    username = authInfo["username"]
    appPass = authInfo["appPass"]
    workspace_id = authInfo["workspace_id"]
    project_id = authInfo["project_id"]
    use_template = args.templateRepo.lower() == "true"
    template_repo = authInfo["template_repo"] if use_template else ""

    extra_info = f"[Use template project {template_repo}]" if use_template else ""
    print(f"[BitBucket] creating {repo_name} Project in Bitbucket {extra_info}")

    successful, msg = create_repo(
        username,
        appPass,
        repo_name,
        workspace_id,
        project_id,
        template_repo=template_repo,
    )
    if successful:
        print(f"[Bitbucket] {repo_name} created successfully.{extra_info}")
    else:
        formatted_msg = jsonfile.beautify(msg)
        print(f"[Bitbucket] {repo_name} created failed. Details:\n{formatted_msg}")


if __name__ == "__main__":
    main()
