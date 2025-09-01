"""
`jobman` is a job management package designed to submit and monitor jobs on remote machines. It is built on the top of the [dpdispatcher](https://docs.deepmodeling.com/projects/dpdispatcher) package.

`jobman` is designed for the big data era, where the number of remoted jobs is large that handling them manually is almost impossible. Imaging that you have more than 1000 jobs to run, you have access to 3 remote high-performance computing (HPC) serves with different computing environment, and you need to monitor the progress of each job, check the output files, and download the results. This is a tedious and time-consuming task. The `jobman` package is designed to automate such tasks. `jobman` will handle the input files, submit the jobs to remote machines, monitor the progress of each job, and download the results to the local machine whenever jobs finished.


Case 1: Distribute jobs to single remote machines

This is used for general purpose, which can define the task_list flexibly where each task can have different command_list, forward_files, backward_files. Just need to:

- Define the `task_list` as a list of [Task](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/task.html) objects.
- Use function [submit_job_chunk()](#submit_job_chunk) to submit jobs to remote machines.

```python
from thkit.jobman import submit_job_chunk, Task
from thkit.config import load_config

mdict = load_config("remote_machine.yml")  # load the remote machine config
task_list = [Task(...), Task(...), ...]    # list of Task objects
submit_job_chunk(
    mdict=mdict,
    work_dir=work_dir,
    task_list=task_list,
    forward_common_files=forward_common_files,
    backward_common_files=backward_common_files,
)
```

Case 2: Distribute jobs to multiple remote machines

This is used for specific purpose (e.g., `alff` package), where the jobs have the same forward_files, backward_files; but the command_list can be different based on computing environment on each remote machine. Just need to:

- Prepare the `task_dirs`, where all of them have the same forward_files, backward_files.
- Define a `prepare_command_list()` function to prepare the command_list for each remote machine.

```python
from thkit.jobman import alff_submit_job_multi_remotes
from thkit.config import load_config
import asyncio

mdict = load_config("remote_machine.yml")  # load the remote machine config

### Prepare command_list on each machine
def prepare_command_list(machine: dict) -> list:
    command_list = []
    dft_cmd = machine.get("command", "python")
    dft_cmd = f"{dft_cmd} ../cli_gpaw_optimize.py ../{FILE_ARG_ASE}"  # `../` to run file in common directory
    command_list.append(dft_cmd)
    return command_list

### Submit to multiple machines
asyncio.run(
    alff_submit_job_multi_remotes(
        multi_mdict=mdict,
        prepare_command_list=prepare_command_list,
        work_dir=work_dir,
        task_dirs=task_dirs,
        forward_files=forward_files,
        backward_files=backward_files,
        forward_common_files=forward_common_files,
        mdict_prefix="dft",
        Logger=Logger,
    )
)
```

Note:
    - Setting remote machines follow the [remote machine schema](https://thangckt.github.io/thkit_doc/schema_doc/config_remote_machine/).
    - Can import from `jobman` these classes: [Task](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/task.html), [Machine](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/machine.html), [Resources](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/resources.html), [Submission](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/api/dpdispatcher.html#dpdispatcher.Submission).
    - To handle if some tasks is finished and some tasks are not finished, see the function [handle_submission()](https://github.com/deepmodeling/dpdispatcher/blob/d55b3c3435a6b4cb8e200682a39a3418fd04d922/dpdispatcher/entrypoints/submission.py#L9)
"""

from thkit.pkg import check_package, create_logger

# check_package("dpdispatcher", auto_install=True)
check_package(
    "dpdispatcher",
    auto_install=True,
    git_repo="https://github.com/thangckt/dpdispatcher.git@master",
)

import asyncio
import datetime
import logging
import time
import warnings
from copy import deepcopy
from math import ceil
from pathlib import Path

import yaml
from dpdispatcher import Machine, Resources, Submission, Task
from dpdispatcher.dlog import dlog
from dpdispatcher.entrypoints.submission import handle_submission

from thkit import THKIT_ROOT
from thkit.config import validate_config
from thkit.stuff import chunk_list, text_color


#####SECTION Dispatching jobs
def _prepare_submission(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    create_remote_path: bool = True,
) -> Submission:
    """Function to simplify the preparation of the [Submission](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/api/dpdispatcher.html#dpdispatcher.Submission) object for dispatching jobs.

    Args:
        mdict (dict): a dictionary contain settings of the remote machine. The parameters described in [here](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/machine.html)
        create_remote_path (bool): whether to create the remote path if it does not exist.
    """
    machine_dict = mdict["machine"]
    resources_dict = mdict["resources"]

    ### revise input path to absolute path and as_string
    abs_machine_dict = machine_dict.copy()
    abs_machine_dict["local_root"] = Path("./").resolve().as_posix()

    ### Create remote_path if not exist
    if create_remote_path:
        execute_command = machine_dict.get("remote_profile").get("execute_command", "")
        remote_path = machine_dict.get("remote_root")
        abs_machine_dict["remote_profile"]["execute_command"] = (
            f"{execute_command} && ([! -d {remote_path}] && mkdir -p {remote_path}) "
        )

    submission = Submission(
        machine=Machine.load_from_dict(abs_machine_dict),
        resources=Resources.load_from_dict(resources_dict),
        work_base=work_dir,
        task_list=task_list,
        forward_common_files=forward_common_files,
        backward_common_files=backward_common_files,
    )
    return submission


#####ANCHOR Synchronous submission
def submit_job_chunk(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    machine_index: int = 0,
    Logger: object = None,
):
    """Function to submit a jobs to the remote machine. The function will:

    - Prepare the task list
    - Make the submission of jobs to remote machines
    - Wait for the jobs to finish and download the results to the local machine

    Args:
        mdict (dict): a dictionary contain settings of the remote machine. The parameters described in the [remote machine schema](https://thangckt.github.io/thkit_doc/schema_doc/config_remote_machine/). This dictionary defines the login information, resources, execution command, etc. on the remote machine.
        task_list (list[Task]): a list of [Task](https://docs.deepmodeling.com/projects/dpdispatcher/en/latest/task.html) objects. Each task object contains the command to be executed on the remote machine, and the files to be copied to and from the remote machine. The dirs of each task must be relative to the `work_dir`.
        forward_common_files (list[str]): common files used for all tasks. These files are i n the `work_dir`.
        backward_common_files (list[str]): common files to download from the remote machine when the jobs are finished.
        machine_index (int): index of the machine in the list of machines.
        Logger (object): the logger object to be used for logging.

    Note:
        - Split the `task_list` into chunks to control the number of jobs submitted at once.
        - Should not use the `Local` contexts, it will interference the current shell environment which leads to the unexpected behavior on local machine. Instead, use another account to connect local machine with `SSH` context.
    """
    if Logger is None:
        Logger = _init_default_logger()

    num_tasks = len(task_list)
    machine_dict = mdict["machine"]
    text = text_color(
        f"Assigned {num_tasks} jobs to Machine {machine_index} \n{_remote_info(machine_dict)}",
        color=_COLOR_MAP[machine_index],
    )
    Logger.info(text)

    ### Divide task_list into chunks
    job_limit = mdict.get("job_limit", 5)
    chunks = chunk_list(task_list, job_limit)
    old_time = None
    for chunk_index, task_list_current_chunk in enumerate(chunks):
        num_tasks_current_chunk = len(task_list_current_chunk)
        new_time = time.time()
        text = _info_current_dispatch(
            num_tasks,
            num_tasks_current_chunk,
            job_limit,
            chunk_index,
            old_time,
            new_time,
        )
        Logger.info(text)
        submission = _prepare_submission(
            mdict=mdict,
            work_dir=work_dir,
            task_list=task_list_current_chunk,
            forward_common_files=forward_common_files,
            backward_common_files=backward_common_files,
        )
        try:
            submission.run_submission()
        except Exception as e:
            handle_submission(submission_hash=submission.get_hash(), download_finished_task=True)
            err_text = f"Machine {machine_index} has error job: \n\t{e}"
            Logger.error(text_color(err_text, color=_COLOR_MAP[machine_index]))
        old_time = new_time
    return


#####ANCHOR Asynchronous submission
_machine_locks = {}  # Dictionary to store per-machine locks


def _get_machine_lock(machine_index):
    if machine_index not in _machine_locks:
        _machine_locks[machine_index] = asyncio.Lock()
    return _machine_locks[machine_index]


async def _run_submission_wrapper(submission, Logger, check_interval=30, machine_index=0):
    """Ensure only one instance of 'submission.run_submission' runs at a time.
    - If use one global lock for all machines, it will prevent concurrent execution of submissions on different machines. Therefore, each machine must has its own lock, so different machines can process jobs in parallel.
    """
    lock = _get_machine_lock(machine_index)  # Get per-machine lock
    async with lock:  # Prevents concurrent execution
        try:
            await asyncio.to_thread(submission.run_submission, check_interval=check_interval)
        except Exception as e:
            await asyncio.to_thread(
                handle_submission,
                submission_hash=submission.get_hash(),
                download_finished_task=True,
            )
            err_text = f"Machine {machine_index} has error job: \n\t{e}"
            Logger.error(text_color(err_text, color=_COLOR_MAP[machine_index]))
        finally:
            del submission  # free up memory
    return


async def async_submit_job_chunk(
    mdict: dict,
    work_dir: str,
    task_list: list[Task],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    machine_index: int = 0,
    Logger: object = None,
):
    """Convert `submit_job_chunk()` into an async function but only need to wait for the completion of the entire `for` loop (without worrying about the specifics of each operation inside the loop)

    Note:
        - An async function normally contain a `await ...` statement to be awaited (yield control to event loop)
        - If the 'event loop is blocked' by a asynchronous function (it will not yield control to event loop), the async function will wait for the completion of the synchronous function. So, the async function will not be executed asynchronously. Try to use `await asyncio.to_thread()` to run the synchronous function in a separate thread, so that the event loop is not blocked.
    """
    if Logger is None:
        Logger = _init_default_logger()

    num_tasks = len(task_list)
    machine_dict = mdict["machine"]
    text = text_color(
        f"Assigned {num_tasks} jobs to Machine {machine_index} \n{_remote_info(machine_dict)}",
        color=_COLOR_MAP[machine_index],
    )
    Logger.info(text)

    ### Divide task_list into chunks
    job_limit = mdict.get("job_limit", 5)
    chunks = chunk_list(task_list, job_limit)
    timer = {f"oldtime_{machine_index}": None}  # dynamic variable name
    for chunk_index, task_list_current_chunk in enumerate(chunks):
        num_tasks_current_chunk = len(task_list_current_chunk)
        timer[f"newtime_{machine_index}"] = time.time()
        text = _info_current_dispatch(
            num_tasks,
            num_tasks_current_chunk,
            job_limit,
            chunk_index,
            timer[f"oldtime_{machine_index}"],
            timer[f"newtime_{machine_index}"],
            machine_index,
        )
        Logger.info(text)
        submission = _prepare_submission(
            mdict=mdict,
            work_dir=work_dir,
            task_list=task_list_current_chunk,
            forward_common_files=forward_common_files,
            backward_common_files=backward_common_files,
        )
        # await asyncio.to_thread(submission.run_submission, check_interval=30)  # this is old, may cause (10054) error
        await _run_submission_wrapper(submission, Logger, 30, machine_index)
        timer[f"oldtime_{machine_index}"] = timer[f"newtime_{machine_index}"]
    Logger.info(
        text_color(f"Machine {machine_index} finished all jobs.", color=_COLOR_MAP[machine_index])
    )
    return


#####!SECTION


#####SECTION Support functions used for `alff` package
def _alff_prepare_task_list(
    command_list: list[str],
    task_dirs: list[str],
    forward_files: list[str],
    backward_files: list[str],
    outlog: str,
    errlog: str,
    # delay_fail_report: bool = True,
) -> list[Task]:
    """Prepare the task list for alff package.

    The feature of jobs in `alff` package are they have the same: command_list, forward_files, backward_files. So this function is to shorthand prepare the list of Task object for `alff` package. For general usage, should prepare the task list from scratch.

    Args:
        command_list (list[str]): the list of commands to be executed on the remote machine.
        task_dirs (list[str]): the list of directories for each task. They must be relative to the `work_dir` in function `_prepare_submission`
        forward_files (list[str]): the list of files to be copied to the remote machine. These files must existed in each `task_dir`.
        backward_files (list[str]): the list of files to be copied back from the remote machine.
        outlog (str): the name of the output log file.
        errlog (str): the name of the error log file.
        # delay_fail_report (bool): whether to delay the failure report until all tasks are done. This is useful when there are many tasks, and we want to wait all tasks finished instead of "the controller interupts if one task fail".

    Returns:
        list[Task]: a list of Task objects.
    """
    command = " &&\n".join(command_list)
    # if delay_fail_report:
    #     command = f"({command}) || :"  # this treat fail jobs as finished jobs -> should not be used.

    ### Define the task_list
    task_list = [None] * len(task_dirs)
    for i, path in enumerate(task_dirs):
        task_list[i] = Task(
            command=command,
            task_work_path=path,
            forward_files=forward_files,
            backward_files=backward_files,
            outlog=outlog,
            errlog=errlog,
        )
    return task_list


#####ANCHOR Submit to multiple machines
async def alff_submit_job_multi_remotes(
    multi_mdict: dict,
    prepare_command_list: callable,
    work_dir: str,
    task_dirs: list[str],
    forward_files: list[str],
    backward_files: list[str],
    forward_common_files: list[str] = [],
    backward_common_files: list[str] = [],
    mdict_prefix: str = "dft",
    Logger: object = None,
):
    """Submit jobs to multiple machines asynchronously.

    Args:
        multi_mdict (dict): the big_dict contains multiple `mdicts`. Each `mdict` contains parameters of one remote machine, which parameters as in the [remote machine schema](https://thangckt.github.io/thkit_doc/schema_doc/config_remote_machine/).
        prepare_command_list(callable): a function to prepare the command list based on each remote machine.
        mdict_prefix(str): the prefix to select remote machines for the same purpose. Example: 'dft', 'md', 'train'.
    """
    if Logger is None:
        Logger = _init_default_logger()

    remote_machine_list = [v for k, v in multi_mdict.items() if k.startswith(mdict_prefix)]
    assert len(remote_machine_list) > 0, (
        f"No remote machines found for the mdict_prefix: {mdict_prefix}"
    )

    num_machines = len(remote_machine_list)
    Logger.info(f"Distribute {len(task_dirs)} jobs across {num_machines} remote machines")

    remain_task_dirs = deepcopy(task_dirs)
    background_runs = []
    for i, current_mdict in enumerate(remote_machine_list):
        current_work_load = current_mdict.get("work_load_ratio", None)

        ### Divide task_dirs
        if not current_work_load:
            current_work_load = 1.0 / num_machines
            num_jobs = ceil(len(remain_task_dirs) * current_work_load)
        else:
            num_jobs = ceil(len(task_dirs) * current_work_load)

        if num_jobs <= len(remain_task_dirs):
            current_task_dirs = remain_task_dirs[:num_jobs]
            remain_task_dirs = remain_task_dirs[num_jobs:]
            num_machines -= 1
        else:
            current_task_dirs = remain_task_dirs
            remain_task_dirs = []

        ### Prepare task_list
        command_list = prepare_command_list(current_mdict)
        task_list = _alff_prepare_task_list(
            command_list=command_list,
            task_dirs=current_task_dirs,
            forward_files=forward_files,
            backward_files=backward_files,
            outlog=f"{mdict_prefix}_out.log",
            errlog=f"{mdict_prefix}_err.log",
        )

        ### Submit jobs
        if len(current_task_dirs) > 0:
            async_task = async_submit_job_chunk(
                mdict=current_mdict,
                work_dir=work_dir,
                task_list=task_list,
                forward_common_files=forward_common_files,
                backward_common_files=backward_common_files,
                machine_index=i,
                Logger=Logger,
            )
            background_runs.append(async_task)
            # Logger.debug(f"Assigned coroutine to Machine {i}: {async_task}")
    await asyncio.gather(*background_runs)
    return


#####!SECTION


#####ANCHOR Change the path of logfile
# "%Y%b%d_%H%M%S" "%Y%m%d_%H%M%S"
_DEFAULT_LOG_FILE = f"{time.strftime('%y%b%d_%H%M%S')}_dispatch.log"


def change_logpath_dispatcher(newlogfile: str = _DEFAULT_LOG_FILE):
    """Change the logfile of dpdispatcher."""
    try:
        for hl in dlog.handlers[:]:  # Remove all old handlers
            hl.close()
            dlog.removeHandler(hl)

        fh = logging.FileHandler(newlogfile)
        # fmt = logging.Formatter(
        #     "%(asctime)s | %(name)s-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        # )
        fmt = logging.Formatter(
            "%(asctime)s | dispatch-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        )
        fh.setFormatter(fmt)
        dlog.addHandler(fh)
        dlog.info(f"LOG INIT: dispatcher log direct to {newlogfile}")

        ### Remove the old log file if it exists
        if Path("./dpdispatcher.log").is_file():
            Path("./dpdispatcher.log").unlink()
    except Exception as e:
        warnings.warn(f"Error during change logfile_path {e}. Use the original path.")
    return


#####ANCHOR helper functions
_COLOR_MAP = {
    0: "blue",
    1: "green",
    2: "yellow",
    3: "magenta",
    4: "cyan",
    5: "red",
    6: "white",
    7: "white",
    8: "white",
    9: "white",
    10: "white",
}


def _info_current_dispatch(
    num_tasks: int,
    num_tasks_current_chunk: int,
    job_limit,
    chunk_index,  # start from 0
    old_time=None,
    new_time=None,
    machine_index=0,
) -> str:
    """Return the information of the current chunk of tasks."""
    total_chunks = ceil(num_tasks / job_limit)
    remaining_tasks = num_tasks - chunk_index * job_limit
    text = f"Machine {machine_index} is handling {num_tasks_current_chunk}/{remaining_tasks} jobs [chunk {chunk_index + 1}/{total_chunks}]."
    ### estimate time remaining
    if old_time is not None and new_time is not None:
        time_elapsed = new_time - old_time
        time_remain = time_elapsed * (total_chunks - chunk_index)
        delta_str = str(datetime.timedelta(seconds=time_remain)).split(".", 2)[0]
        text += f" ETC {delta_str}"
    text = text_color(text, color=_COLOR_MAP[machine_index])  # make color
    return text


def _remote_info(machine_dict) -> str:
    """Return the remote machine information.
    Args:
        mdict (dict): the machine dictionary
    """
    remote_path = machine_dict["remote_root"]
    hostname = machine_dict["remote_profile"]["hostname"]
    info_text = f"{' ' * 12}Remote host: {hostname}\n"
    info_text += f"{' ' * 12}Remote path: {remote_path}"
    return info_text


def _init_default_logger(logfile: str = _DEFAULT_LOG_FILE):
    """Initialize the default logger not provided"""
    Path("log").mkdir(parents=True, exist_ok=True)  # create log directory
    time_str = time.strftime("%y%m%d_%H%M%S")  # "%y%b%d" "%Y%m%d"
    DEFAULT_LOGFILE = f"job/{time_str}_jobman.log"

    Logger = create_logger("alff", level="INFO", log_file=DEFAULT_LOGFILE)
    change_logpath_dispatcher(DEFAULT_LOGFILE)
    return Logger


def validate_machine_config(machine_file: str):
    """Validate the YAML file contains machine config. The top-level keys should start with:
    - `train_1`, `train_2`,... for training jobs
    - `lammps_1`, `lammps_2`,... for lammps jobs
    - `gpaw_1`, `gpaw_2`,... for gpaw jobs
    """
    SCHEMA_MACHINE_FILE = f"{THKIT_ROOT}/schema/schema_remote_machine.yml"
    schema = yaml.safe_load(open(SCHEMA_MACHINE_FILE))
    config = yaml.safe_load(open(machine_file))
    for k, v in config.items():
        validate_config(config_dict={k: v}, schema_dict={k: schema["tha"]})

    # for k, v in config.items():
    #     if k.startswith("md"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["tha"]})
    #     elif k.startswith("train"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["train"]})
    #     elif k.startswith("dft"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["dft"]})
    return
