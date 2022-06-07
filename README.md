The Simplest and Most Powerful Concurrent Helper
===============

Setup
----------
```bash
pip install concurrent_helper
```


2 Core Functions: run_with_concurrent & run_with_message_queue
----------

```python
def run_with_concurrent(
    func,
    args_list,
    concurrent_type="thread",  # ["single", "thread", "process", "x-process"]
    concurrent_num=1,
    show_process="",  # ["", "tqdm", "print"]
    show_interval=1,
    raise_exception=True,
):
    pass

def run_with_message_queue(
    init_func,
    init_args_list,
    func,
    args_list,
):
    pass
```


Key Params
----------

concurrent_type:
| type        | Description                 |
| ----------- | ----------------------------|
| single      | like normal for-loop        |
| thread      | thread pool                 |
| process     | process pool                |
| x-process   | multi independent process   |


Examples
----------
```python
import concurrent_helper
import os


def init(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)


def work(task_id):
    print("{}: I am working on {} for {}".format(
        os.getpid(),
        os.environ.get("CUDA_VISIBLE_DEVICES"),
        task_id)
    )
    return task_id * 2


rtvs = concurrent_helper.run_with_concurrent(work, list(range(10)), "x-process")
print("----")
rtvs = concurrent_helper.run_with_concurrent(work, list(range(10)), "process")
print("----")
rtvs = concurrent_helper.run_with_concurrent(work, list(range(10)), "thread")
print("----")
rtvs = concurrent_helper.run_with_message_queue(
    init, list(range(3)), 
    work, list(range(10))
)
print(rtvs)
```

outputs:
```bash
90746: I am working on None for 0
90747: I am working on None for 1
90748: I am working on None for 2
90749: I am working on None for 3
90750: I am working on None for 4
90751: I am working on None for 5
90752: I am working on None for 6
90753: I am working on None for 7
90754: I am working on None for 8
90755: I am working on None for 9
----
90756: I am working on None for 0
90756: I am working on None for 1
90756: I am working on None for 2
90756: I am working on None for 3
90756: I am working on None for 4
90756: I am working on None for 5
90756: I am working on None for 6
90756: I am working on None for 7
90756: I am working on None for 8
90756: I am working on None for 9
----
90743: I am working on None for 0
90743: I am working on None for 1
90743: I am working on None for 2
90743: I am working on None for 3
90743: I am working on None for 4
90743: I am working on None for 5
90743: I am working on None for 6
90743: I am working on None for 7
90743: I am working on None for 8
90743: I am working on None for 9
----
90760: I am working on 0 for 0
90761: I am working on 1 for 1
90762: I am working on 2 for 2
[    1/10   ] ...... Fns work with run_with_message_queue ...... in     0.0073 seconds.
[    2/10   ] ...... Fns work with run_with_message_queue ...... in     0.0068 seconds.
[    3/10   ] ...... Fns work with run_with_message_queue ...... in     0.0067 seconds.
90763: I am working on 0 for 3
90764: I am working on 1 for 4
[    4/10   ] ...... Fns work with run_with_message_queue ...... in     0.0055 seconds.
90765: I am working on 2 for 5
[    5/10   ] ...... Fns work with run_with_message_queue ...... in     0.0053 seconds.
[    6/10   ] ...... Fns work with run_with_message_queue ...... in     0.0054 seconds.
90766: I am working on 0 for 6
90767: I am working on 2 for 7
[    7/10   ] ...... Fns work with run_with_message_queue ...... in     0.0051 seconds.
90768: I am working on 0 for 8
[    8/10   ] ...... Fns work with run_with_message_queue ...... in     0.0053 seconds.
[    9/10   ] ...... Fns work with run_with_message_queue ...... in     0.0053 seconds.
90769: I am working on 2 for 9
[   10/10   ] ...... Fns work with run_with_message_queue ...... in     0.0050 seconds.
>>>>>> Fns 10 work with run_with_message_queue total use     0.0272 seconds.
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```
