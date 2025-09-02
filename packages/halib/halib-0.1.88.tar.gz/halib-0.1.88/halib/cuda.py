import importlib
from rich.pretty import pprint
from rich.console import Console

console = Console()


def tcuda():
    NOT_INSTALLED = "Not Installed"
    GPU_AVAILABLE = "GPU(s) Available"
    ls_lib = ["torch", "tensorflow"]
    lib_stats = {lib: NOT_INSTALLED for lib in ls_lib}
    for lib in ls_lib:
        spec = importlib.util.find_spec(lib)
        if spec:
            if lib == "torch":
                import torch

                lib_stats[lib] = str(torch.cuda.device_count()) + " " + GPU_AVAILABLE
            elif lib == "tensorflow":
                import tensorflow as tf

                lib_stats[lib] = (
                    str(len(tf.config.list_physical_devices("GPU")))
                    + " "
                    + GPU_AVAILABLE
                )
    console.rule("<CUDA Library Stats>")
    pprint(lib_stats)
    console.rule("</CUDA Library Stats>")
    return lib_stats


def main():
    tcuda()


if __name__ == "__main__":
    main()
