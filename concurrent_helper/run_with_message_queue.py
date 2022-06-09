# -*- coding: utf-8 -*-

"""
Authors:
    chuanqi.tan ### gmail ### com

The Simplest and Most Powerful Concurrent Helper
"""

import time
import sys
from multiprocessing import Process, Queue

from .run_with_concurrent import run_with_concurrent
from .process_bar import make_process_bar

if sys.version_info.major == 2:
    import Queue as Q
else:
    import queue as Q


def _run_with_mq_server(init_func, init_args, func, task_q, result_q):
    if type(init_args) != tuple:
        init_args = (init_args,)
    init_func(*init_args)

    while True:
        try:
            idx, args = task_q.get(block=False)
            start_time = time.time()
            rtv = run_with_concurrent(func, [args,], "x-process", 1,)
            used_time = time.time() - start_time
            result_q.put((used_time, idx, rtv[0]))
        except Q.Empty as _:
            break


def _run_with_mq_collect_result(
    result_q, total_num, func_name, show_process, show_interval
):
    total_rtv = [None] * total_num
    finish_num = 0
    pbar = make_process_bar(
        total_num, show_process, show_interval, func_name, "run_with_message_queue"
    )

    while finish_num < total_num:
        used_time, idx, rtv = result_q.get()
        total_rtv[idx] = rtv
        finish_num += 1
        pbar.update(used_time)

    pbar.close()
    return total_rtv


def run_with_message_queue(
    init_func,
    init_args_list,  # it will set concurrent_num == len(init_args_list)
    func,
    args_list,
    show_process="print",  # ["", "tqdm", "print"]
    show_interval=0.01,
):
    if show_interval < 1:
        show_interval = int(len(args_list) * show_interval)
    show_interval = max(1, show_interval)

    result_q = Queue()
    task_q = Queue()
    for idx, args in enumerate(args_list):
        task_q.put((idx, args))

    running_servers = []
    for i in range(len(init_args_list)):
        p = Process(
            target=_run_with_mq_server,
            args=(init_func, init_args_list[i], func, task_q, result_q),
        )
        p.start()
        running_servers.append(p)

    total_rtvs = _run_with_mq_collect_result(
        result_q, len(args_list), func.__name__, show_process, show_interval
    )
    for server in running_servers:
        server.terminate()

    return total_rtvs
