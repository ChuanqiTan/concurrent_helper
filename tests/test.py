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
