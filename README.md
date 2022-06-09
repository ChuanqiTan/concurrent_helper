The Simplest and Most Powerful Concurrent Helper
===============

Setup
===============
```bash
pip install concurrent-helper
```


Key Features
===============

- Simplest and powerful, very easy to use.
- Works well both on ``Python2`` and ``Python3``.
- Support for multiple concurrent modes: ``thread pool, process pool and independent multi-processes``.
- Support the mode of ``Message Queue + Service``.
- Multiple progress bar display modes.


Quick Start
===============
```python
import concurrent_helper
import os


def init(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)


def work(task_id, gpu_id=None):
    if gpu_id is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    print("{}: I am working on {} for {}".format(
        os.getpid(),
        os.environ.get("CUDA_VISIBLE_DEVICES"),
        task_id)
    )
    return task_id * 2


total_gpu_num = 3
todos = [(x, x % total_gpu_num) for x in range(10)]

rtvs = concurrent_helper.run_with_concurrent(work, todos, "thread")
rtvs = concurrent_helper.run_with_concurrent(work, todos, "process")
rtvs = concurrent_helper.run_with_concurrent(work, todos, "x-process")

rtvs = concurrent_helper.run_with_message_queue(
    init, list(range(3)),   # start 3 services
    work, list(range(10))   # has 10 tasks to do
)
```


Core Function: run_with_concurrent
===============

```python
def run_with_concurrent(
    func,
    args_list,
    concurrent_type="thread",  # ["single", "thread", "process", "x-process"]
    concurrent_num=1,
    show_process="print",  # ["", "tqdm", "print"]
    show_interval=0.01,
):
    pass
```

Run a function by concurrent mode.


Key Params
--------------

``concurrent_type``:

| Param Value | Description                 |
| ----------- | ----------------------------|
| single      | like normal for-loop        |
| thread      | thread pool                 |
| process     | process pool                |
| x-process   | independent multi-processes |

Warning:

> Arrocding to this issue: <https://github.com/agronholm/pythonfutures/issues/29>, there is a bug in ``concurrent.futures`` of Python2.
The relevant fix upstream uses Python 3 features and cannot be backported.

> This bug only happen when child-process killed by system (for exapmle, memory overflow). If you encounter this problem, use the ``x-process`` instead of ``process`` when you are using Python2.


``show_process``:

| Param Value | Description                 |
| ----------- | ----------------------------|
| ""          | don't show process          |
| tqdm        | use tqdm style process bar  |
| print       | print process bar info      |

Warning:

> Please note that tqdm is not thread safe, use print if you need the guarantee of thread safe.


``show_interval``:

| Param Value | Description                         |
| ----------- | ------------------------------------|
| >= 1        | update progress bar by every N task |
| < 1         | update progress bar by percentage   |


Core Function: run_with_message_queue
===============

```python
def run_with_message_queue(
    init_func,
    init_args_list,  # concurrent_num == len(init_args_list)
    func,
    args_list,
    show_process="print",  # ["", "tqdm", "print"]
    show_interval=0.01,
):
    pass
```

Run function by ``Message Queue + Service`` mode.

> Fist, start N (``N=len(init_args_list)``) services, these services will inited by ``init_func``. 
> 
> After that, these services will obtain M (``M=len(args_list)``) tasks from message queue and run these by ``func``.

Why we need ``Message Queue + Service`` mode?

> In order to maximize resource utilization (like GPU), we should to start a certain number of services according to the number of resources. Then, these services will obtain tasks from the message queue and run them.


Examples
===============
```python
import concurrent_helper
import os


def init(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)


def work(task_id, gpu_id=None):
    if gpu_id is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    print("{}: I am working on {} for {}".format(
        os.getpid(),
        os.environ.get("CUDA_VISIBLE_DEVICES"),
        task_id)
    )
    return task_id * 2


total_gpu_num = 3
todos = [(x, x % total_gpu_num) for x in range(5)]

rtvs = concurrent_helper.run_with_concurrent(work, todos, "thread", 3)
print("----")
rtvs = concurrent_helper.run_with_concurrent(work, todos, "process", 3)
print("----")
rtvs = concurrent_helper.run_with_concurrent(work, todos, "x-process", 3, "tqdm")
print("----")
rtvs = concurrent_helper.run_with_message_queue(
    init, list(range(3)),
    work, list(range(5))
)
print(rtvs)
```

outputs:

```bash
37059: I am working on 0 for 0
37059: I am working on 1 for 1
37059: I am working on 2 for 2
[    1/5    ] ...... Fns work with thread ...... in     0.0001 seconds.
37059: I am working on 0 for 3
37059: I am working on 1 for 4
[    2/5    ] ...... Fns work with thread ...... in     0.0001 seconds.
[    3/5    ] ...... Fns work with thread ...... in     0.0003 seconds.
[    4/5    ] ...... Fns work with thread ...... in     0.0002 seconds.
[    5/5    ] ...... Fns work with thread ...... in     0.0001 seconds.
>>>>>> Fns 5 work with thread total use     0.0020 seconds.
----
37063: I am working on 0 for 0
37064: I am working on 1 for 1
37064: I am working on 0 for 3
37065: I am working on 2 for 2
37063: I am working on 1 for 4
[    1/5    ] ...... Fns work with process ...... in     0.0003 seconds.
[    2/5    ] ...... Fns work with process ...... in     0.0003 seconds.
[    3/5    ] ...... Fns work with process ...... in     0.0000 seconds.
[    4/5    ] ...... Fns work with process ...... in     0.0000 seconds.
[    5/5    ] ...... Fns work with process ...... in     0.0006 seconds.
>>>>>> Fns 5 work with process total use     0.0126 seconds.
----
37066: I am working on 0 for 0
37067: I am working on 1 for 1
37068: I am working on 2 for 2
37069: I am working on 0 for 3
37070: I am working on 1 for 4
[work / x-process]: 100%|█████████████████| 5/5 [00:00<00:00, 346.26it/s]
----
37074: I am working on 0 for 0
37075: I am working on 1 for 1
37076: I am working on 2 for 2
[    1/1    ] ...... Fns work with x-process ...... in     0.0003 seconds.
>>>>>> Fns 1 work with x-process total use     0.0085 seconds.
[    1/1    ] ...... Fns work with x-process ...... in     0.0004 seconds.
[    1/5    ] ...... Fns work with run_with_message_queue ...... in     0.0090 seconds.
>>>>>> Fns 1 work with x-process total use     0.0090 seconds.
[    1/1    ] ...... Fns work with x-process ...... in     0.0003 seconds.
>>>>>> Fns 1 work with x-process total use     0.0087 seconds.
[    2/5    ] ...... Fns work with run_with_message_queue ...... in     0.0093 seconds.
[    3/5    ] ...... Fns work with run_with_message_queue ...... in     0.0090 seconds.
37077: I am working on 0 for 3
37078: I am working on 1 for 4
[    1/1    ] ...... Fns work with x-process ...... in     0.0003 seconds.
>>>>>> Fns 1 work with x-process total use     0.0061 seconds.
[    4/5    ] ...... Fns work with run_with_message_queue ...... in     0.0063 seconds.
[    1/1    ] ...... Fns work with x-process ...... in     0.0003 seconds.
>>>>>> Fns 1 work with x-process total use     0.0060 seconds.
[    5/5    ] ...... Fns work with run_with_message_queue ...... in     0.0061 seconds.
>>>>>> Fns 5 work with run_with_message_queue total use     0.0182 seconds.
[0, 2, 4, 6, 8]
```


TODO
===============

- [DONE] Test codes.
- [DONE] Detail docs & English describe about ``run_with_message_queue`` & More code examples.
- [DONE] Add params ``show_process, show_interval`` to ``run_with_message_queue``.
- [DONE] Remove ``raise_exception`` param, it will be default action.
