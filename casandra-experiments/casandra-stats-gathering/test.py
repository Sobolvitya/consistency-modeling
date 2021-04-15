from multiprocessing import Pool
import time
import concurrent.futures

import write_stats_gathering
from modeiling import consistency_level_name_to_value


def f(x):
    print("Evaluating {i}".format(i=x))
    time.sleep(5)
    return x * x


def f1(x):
    print("Evaluating {i}".format(i=x))
    time.sleep(1)
    return x * x


def tst(a: list):
    print("Evaluating {i}".format(i=a[0]))
    time.sleep(20)
    return a[0] * a[0]


def tst1(b: list) -> list:
    time.sleep(3)
    return [len(b)]

def tst2(b: write_stats_gathering.WriteGatheringTask) -> list:
    time.sleep(3)
    return [12]


class MyClass:

    def __init__(self):
        self.a = 1
        self.consistency_level = 123
        self.ip = 123
        self.session = 123
        self.write_delay_s = 123
        self.table_name = 123


def method_name():
    write_task1 = write_stats_gathering.WriteGatheringTask(
        consistency_level=consistency_level_name_to_value["ALL"],
        write_delay_ms=12,
        table_name="table_name",
        node_ip="experiment_data.write_ip"
    )

    write_task2 = write_stats_gathering.WriteGatheringTask(
        consistency_level=consistency_level_name_to_value["ALL"],
        write_delay_ms=12,
        table_name="table_name",
        node_ip="experiment_data.write_ip"
    )

    write_task3 = write_stats_gathering.WriteGatheringTask(
        consistency_level=consistency_level_name_to_value["ALL"],
        write_delay_ms=12,
        table_name="table_name",
        node_ip="experiment_data.write_ip"
    )

    with Pool(processes=4) as pool:
        # res = []
        # for i in range(10):
        #     res.append(pool.apply_async(f, (i,)))

        l1 = [write_task1, write_task2]
        a = [l1, [write_task3]]
        b = list(map(lambda i: i, a))
        r2 = pool.map_async(tst1, b)
        r3 = pool.map_async(tst2, (write_task1,))
        result = pool.apply_async(f1, (10,))  # evaluate "f(10)" asynchronously in a single process
        # r1 = pool.map_async(f, range(3))  # prints "[0, 1, 4,..., 81]"
        # while result.ready() and r1.ready():
        #     time.sleep(10)

        get = r2.get()
        get1 = r3.get()
        print(get)  # prints "100" unless your computer is *very* slow
        result_get = result.get()
        print(result_get)


if __name__ == '__main__':
    method_name()
