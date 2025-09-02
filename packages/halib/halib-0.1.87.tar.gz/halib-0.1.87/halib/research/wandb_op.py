import glob
from rich.pretty import pprint
import os
import subprocess
import argparse
import wandb
from tqdm import tqdm
from rich.console import Console
console = Console()

def sync_runs(outdir):
    outdir = os.path.abspath(outdir)
    assert os.path.exists(outdir), f"Output directory {outdir} does not exist."
    sub_dirs = [name for name in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, name))]
    assert len(sub_dirs) > 0, f"No subdirectories found in {outdir}."
    console.rule("Parent Directory")
    console.print(f"[yellow]{outdir}[/yellow]")

    exp_dirs = [os.path.join(outdir, sub_dir) for sub_dir in sub_dirs]
    wandb_dirs = []
    for exp_dir in exp_dirs:
        wandb_dirs.extend(glob.glob(f"{exp_dir}/wandb/*run-*"))
    if len(wandb_dirs) == 0:
        console.print(f"No wandb runs found in {outdir}.")
        return
    else:
        console.print(f"Found [bold]{len(wandb_dirs)}[/bold] wandb runs in {outdir}.")
        for i, wandb_dir in enumerate(wandb_dirs):
            console.rule(f"Syncing wandb run {i + 1}/{len(wandb_dirs)}")
            console.print(f"Syncing: {wandb_dir}")
            process = subprocess.Popen(
                ["wandb", "sync", wandb_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            for line in process.stdout:
                console.print(line.strip())
                if " ERROR Error while calling W&B API" in line:
                    break
            process.stdout.close()
            process.wait()
            if process.returncode != 0:
                console.print(f"[red]Error syncing {wandb_dir}. Return code: {process.returncode}[/red]")
            else:
                console.print(f"Successfully synced {wandb_dir}.")

def delete_runs(project, pattern=None):
    console.rule("Delete W&B Runs")
    confirm_msg = f"Are you sure you want to delete all runs in"
    confirm_msg += f" \n\tproject: [red]{project}[/red]"
    if pattern:
        confirm_msg += f"\n\tpattern: [blue]{pattern}[/blue]"

    console.print(confirm_msg)
    confirmation = input(f"This action cannot be undone. [y/N]: ").strip().lower()
    if confirmation != "y":
        print("Cancelled.")
        return

    print("Confirmed. Proceeding...")
    api = wandb.Api()
    runs = api.runs(project)

    deleted = 0
    console.rule("Deleting W&B Runs")
    if len(runs) == 0:
        print("No runs found in the project.")
        return
    for run in tqdm(runs):
        if pattern is None or pattern in run.name:
            run.delete()
            console.print(f"Deleted run: [red]{run.name}[/red]")
            deleted += 1

    console.print(f"Total runs deleted: {deleted}")


def valid_argument(args):
    if args.op == "sync":
        assert os.path.exists(args.outdir), f"Output directory {args.outdir} does not exist."
    elif args.op == "delete":
        assert isinstance(args.project, str) and len(args.project.strip()) > 0, "Project name must be a non-empty string."
    else:
        raise ValueError(f"Unknown operation: {args.op}")

def parse_args():
    parser = argparse.ArgumentParser(description="Operations on W&B runs")
    parser.add_argument("-op", "--op", type=str, help="Operation to perform", default="sync", choices=["delete", "sync"])
    parser.add_argument("-prj", "--project", type=str, default="fire-paper2-2025", help="W&B project name")
    parser.add_argument("-outdir", "--outdir", type=str, help="arg1 description", default="./zout/train")
    parser.add_argument("-pt", "--pattern",
        type=str,
        default=None,
        help="Run name pattern to match for deletion",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    # Validate arguments, stop if invalid
    valid_argument(args)

    op = args.op
    if op == "sync":
        sync_runs(args.outdir)
    elif op == "delete":
        delete_runs(args.project, args.pattern)
    else:
        raise ValueError(f"Unknown operation: {op}")

if __name__ == "__main__":
    main()
