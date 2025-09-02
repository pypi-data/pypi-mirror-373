Helper package for coding and automation

**Version 0.1.88**

+ `research/profiler`: add `zProfiler` class to measure execution time of contexts and steps, with support for dynamic color scales in plots.

**Version 0.1.77**

+ `research/base_exp`: add base experiment class to handle common experiment tasks, including performance calculation and saving results.

**Version 0.1.67**

+ now use `uv` for venv management
+ `research/perfcalc`: support both torchmetrics and custom metrics for performance calculation

**Version 0.1.61**

+ add `util/video`: add `VideoUtils` class to handle common video-related tasks
+ add `util/gpu_mon`: add `GPUMonitor` class to monitor GPU usage and performance

**Version 0.1.59**

+ add `util/perfcalc`: abstract class for performance calculation. This class need to be inherited and implemented with specific performance calculation logic.

**Version 0.1.55**

+ add `util/dataclass_util` to help dynamically create `dataclass` classes from dictionary or YAML file, including support for nested dataclasses. From there, we can use `dataclass_wizard` to create a list of `dataclass` classes with the help from ChatGPT.

**Version 0.1.52**

+ add `research/perftb` module to allow creating and managing performance tables for experiments, including filtering by datasets, metrics, and experiments.

**Version 0.1.50**

+ add `pprint_local_path` to print local path (file/directory) in clickable link (as file URI)

+ add `research` package to help with research tasks, including `benchquery` for benchmarking queries from dataframe
+ add `wandb` module to allow easy sync offline data to Weights & Biases (wandb) and batch clear wandb runs.

**Version 0.1.47**
+ add `pprint_box` to print object/string in a box frame (like in `inspect`)

**Version 0.1.46**
+ filter the warning message of `UserWarning: Unable to import Axes3D.`
+ auto_wrap_text for `fn_display_df` to avoid long text in the table

**Version 0.1.42**
+ add <rich_color.py>: add basic color list (for easy usage)

**Version 0.1.41**
+ add <rich_color.py> to display rich color information in <rich> python package (rcolor_str, rcolor_pallet_all, etc.)

**Version 0.1.40**

+  update <csvfile.py> to use `itables` and `pygwalker` to display dataframe in jupyter notebook.

**Version 0.1.38**

+  add <torchloader.py> to search for best cfg for torch dataloader (num_workers, batch_size, pin_memory, et.)

**Version 0.1.37**

+  add <dataset.py> to help split classification dataset into train/val(test)
---
**Version 0.1.33**

+ add `plot.py` module to plot DL model training history (with columlns: epoch, train_accuracy, val_accuracy, train_loss, val_loss) using `seaborn` and `matplotlib`
---
**Version 0.1.29**

+ for `tele_noti` module, `kaleido==0.1.*` is required for plotly since `kaleido 0.2.*` is not working (taking for ever to generate image)
---
**Version 0.1.24**

+ rename `sys` to `system` to avoid conflict with built-in `sys` module
+ add `tele_noti` module to send notification to telegram after a specific interval for training progress monitoring
---
**Version 0.1.22**

+ add `cuda.py` module to check CUDA availability (for both pytorch and tensorflow)
---
**Version 0.1.21**

+ using `networkx` and `omegaconf` to allow yaml file inheritance and override
---
**Version 0.1.15**

+ `__init__.py`: add common logging library; also `console_log` decorator to log function (start and end)

---

**Version 0.1.10**

+ filesys: fix typo on "is_exit" to "is_exist"
+ gdrive: now support uploading file to folder and return direct link (shareable link)

**Version 0.1.9**

+ add dependencies requirement.txt

**Version 0.1.8**

Fix bugs:

+ [performance] instead of inserting directly new rows into table dataframe, first insert it into in-memory `row_pool_dict`, that fill data in that dict into the actual dataframe when needed.

---

**Version 0.1.7**

Fix bugs:

+ fix insert into table so slow by allowing insert multiple rows at once

---

**Version 0.1.6**

New features:

+ add DFCreator for manipulating table (DataFrame) - create, insert row, display, write to file

---

**Version 0.1.5**

New Features

+ add cmd module
+ new package structure

---

**Version 0.1.4**

New Features

+ add support to create Bitbucket Project from template

---

**Version 0.1.2**

New Features

+ add support to upload local to google drive.
