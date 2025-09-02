import subprocess


# @link: https://geekflare.com/learn-python-subprocess/
# subprocess.run(['ls', '-la'])
def run(args):
    process = subprocess.run(args, capture_output=True, text=True)
    return process.returncode
