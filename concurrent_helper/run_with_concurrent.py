# -*- coding: utf-8 -*-

"""
Authors:
    chuanqi.tan ### gmail ### com

The Simplest and Most Powerful Concurrent Helper
"""

import logging
import time
import sys
from collections import OrderedDict
from multiprocessing import Process, Queue
from concurrent import futures

from .process_bar import make_process_bar

if sys.version_info.major == 2:
    import Queue as Q
else:
    import queue as Q


def _run_func_and_time_it(func, *args):
    s = time.time()

    try:
        rtv = func(*args)
    except Exception as e:
        logging.exception(e)
        raise

    e = time.time()
    return e - s, rtv


def independent_process_wrap(func, idx, queue_rtv, *args):
    try:
        rtv = func(*args)
    except Exception as e:
        rtv = (-1, e)

    queue_rtv.put((idx, rtv))


class IndependentExecutor(object):
    def __init__(self, max_workers=1):
        self.max_workers = max_workers
        self.finished_num = 0
        self.todo = []
        self.all_tasks = []
        self.queue_rtv = Queue()
        self.running = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def submit(self, func, *args, **kwargs):
        future = IndependentFuture(
            func, len(self.all_tasks), self.queue_rtv, *args, **kwargs
        )
        self.todo.append(future)
        self.all_tasks.append(future)
        return future


class IndependentFuture(object):
    def __init__(self, func, index, queue_rtv, *args, **kwargs):
        self.p = Process(
            target=independent_process_wrap,
            args=((func, index, queue_rtv) + args),
            kwargs=kwargs,
        )
        self.index = index
        self.rtv = None

    def result(self):
        if isinstance(self.rtv, Exception):
            return self.rtv
        else:
            return self.rtv


class ProcessKilledError(RuntimeError):
    def __init__(self, exitcode):
        super(ProcessKilledError, self).__init__(exitcode)
        self.exitcode = exitcode


def _try_start_new_independent_subprocess(executor):
    if executor.todo:
        future = executor.todo.pop(0)
        future.p.daemon = True
        future.p.start()
        executor.running.add(future.index)


def check_independent_future_as_completed(todo, executor):
    for i in range(executor.max_workers):
        _try_start_new_independent_subprocess(executor)

    while True:
        if executor.finished_num >= len(executor.all_tasks):
            return

        finished_future = None

        for idx in executor.running:
            future = executor.all_tasks[idx]
            if not future.p.is_alive() and future.p.exitcode != 0:
                future.rtv = -1, ProcessKilledError(future.p.exitcode)
                future.p.terminate()
                finished_future = future

                logging.error(
                    "*** Process {} was killed by exitcode ({}) ***".format(
                        future.index, future.p.exitcode
                    )
                )
                break

        if not finished_future:
            try:
                idx, rtv = executor.queue_rtv.get(timeout=1)
                finished_future = executor.all_tasks[idx]
                finished_future.p.join()
                finished_future.rtv = rtv
                finished_future.p.terminate()
            except Q.Empty as e:
                pass

        if finished_future:
            executor.finished_num += 1
            executor.running.remove(finished_future.index)
            _try_start_new_independent_subprocess(executor)
            yield finished_future


class _SingleExecutor(object):
    def __init__(self, max_workers=1):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def submit(self, func, *args, **kwargs):
        return _SingleFuture(func, *args, **kwargs)


class _SingleFuture(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def result(self):
        return self.func(*self.args, **self.kwargs)


def _check_as_compeleted(todo, concurrent_type, executor):
    if concurrent_type == "single":
        for future in todo:
            yield future
    elif concurrent_type == "x-process":
        for future in check_independent_future_as_completed(todo, executor):
            yield future
    else:
        for rtv in futures.as_completed(todo):
            yield rtv


def run_with_concurrent(
    func,
    args_list,
    concurrent_type="thread",  # ["single", "thread", "process", "x-process"]
    concurrent_num=1,
    show_process="print",  # ["", "tqdm", "print"]
    show_interval=0.01,
):
    if not args_list:
        return []

    if concurrent_type == "thread":
        concurrent_executor = futures.ThreadPoolExecutor
    elif concurrent_type == "process":
        concurrent_executor = futures.ProcessPoolExecutor
    elif concurrent_type == "x-process":
        concurrent_executor = IndependentExecutor
    elif concurrent_type == "single":
        concurrent_executor = _SingleExecutor
    else:
        raise ValueError("unknow concurrent type, {}".format(concurrent_type))

    rtv = [None] * len(args_list)
    pbar = make_process_bar(
        len(args_list), show_process, show_interval, func.__name__, concurrent_type
    )

    with concurrent_executor(max_workers=concurrent_num) as executor:
        to_do = OrderedDict()
        for idx, args in enumerate(args_list):
            if type(args) not in (tuple, list):
                args = (args,)
            submit_future = executor.submit(_run_func_and_time_it, func, *args)
            submit_future.index = idx
            to_do[submit_future] = idx

        for fns_idx, future in enumerate(
            _check_as_compeleted(to_do, concurrent_type, executor), 1
        ):
            used_time, real_rtv = future.result()
            rtv[to_do[future]] = real_rtv
            pbar.update(used_time)

    pbar.close()
    return rtv
