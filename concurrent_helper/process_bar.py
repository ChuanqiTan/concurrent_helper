# -*- coding: utf-8 -*-

"""
Authors:
    chuanqi.tan ### gmail ### com

The Simplest and Most Powerful Concurrent Helper
"""

import time

from tqdm import tqdm


class EmptyProcessBar(object):
    def __init__(self, total, func_name, concurrent_type, show_interval):
        pass

    def update(self, used_time):
        pass

    def close(self):
        pass


class TqdmProcessBar(object):
    def __init__(self, total, func_name, concurrent_type, show_interval):
        self.pbar = tqdm(
            total=total, desc="[{} / {}]".format(func_name, concurrent_type)
        )

    def update(self, used_time):
        self.pbar.update(1)

    def close(self):
        self.pbar.close()


class PrintProcessBar(object):
    def __init__(self, total, func_name, concurrent_type, show_interval):
        self.start_time = time.time()
        self.total_num = total
        self.func_name = func_name
        self.concurrent_type = concurrent_type
        self.finished_num = 0

        if show_interval < 1:
            show_interval = int(self.total_num * show_interval)
        self.show_interval = max(1, show_interval)

    def update(self, used_time):
        self.finished_num += 1
        self.finished_num = min(self.finished_num, self.total_num)

        if (
            self.finished_num % self.show_interval == 0
            or self.finished_num == self.total_num
        ):
            print(
                "[{:>5}/{:<5}] ...... Fns {} with {} ...... in {:>10.4f} seconds.".format(
                    self.finished_num,
                    self.total_num,
                    self.func_name,
                    self.concurrent_type,
                    used_time,
                )
            )

    def close(self):
        time_used = time.time() - self.start_time
        if time_used <= 100:
            time_str = "{:>10.4f} seconds".format(time_used)
        else:
            time_str = "{:>10.4f} minutes".format(time_used / 60.0)

        print(
            ">>>>>> Fns {} {} with {} total use {}.".format(
                self.total_num, self.func_name, self.concurrent_type, time_str
            )
        )


def make_process_bar(
    total_num, show_process, show_interval, func_name, concurrent_type
):
    if show_process == "tqdm":
        pbar = TqdmProcessBar(total_num, func_name, concurrent_type, show_interval)
    elif show_process == "print":
        pbar = PrintProcessBar(total_num, func_name, concurrent_type, show_interval)
    else:
        pbar = EmptyProcessBar(total_num, func_name, concurrent_type, show_interval)

    return pbar
