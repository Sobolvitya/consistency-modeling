import concurrent.futures
import logging
import os
import time
from multiprocessing import Pool
from typing import List

from cassandra import ConsistencyLevel

import experiments_data_objects
import read_stats_gathering
import write_stats_gathering
from commons import chunks

log_format = '[PID - %(process)d] %(asctime)s: %(message)s'
logging.basicConfig(
    format=log_format,
    level=logging.DEBUG,
    datefmt="%H:%M:%S"
)

consistency_level_name_to_value = {
    'ANY': ConsistencyLevel.ANY,
    'ONE': ConsistencyLevel.ONE,
    'TWO': ConsistencyLevel.TWO,
    'THREE': ConsistencyLevel.THREE,
    'QUORUM': ConsistencyLevel.QUORUM,
    'ALL': ConsistencyLevel.ALL,
    'LOCAL_QUORUM': ConsistencyLevel.LOCAL_QUORUM,
    'EACH_QUORUM': ConsistencyLevel.EACH_QUORUM,
    'SERIAL': ConsistencyLevel.SERIAL,
    'LOCAL_SERIAL': ConsistencyLevel.LOCAL_SERIAL,
    'LOCAL_ONE': ConsistencyLevel.LOCAL_ONE
}

default_table_name = 'Records{id}.tbl_Records{id}'
default_results_file_name = "experiment_{id}_results.txt"


def read_func(read_tasks: List[read_stats_gathering.ReadGatheringTask], iterations: int) -> dict:
    logging.info("Start processing read tasks of size - {size} in pid - {pid}"
                 .format(size=len(read_tasks), pid=os.getpid()))

    read_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(read_tasks)) as executor:
        read_futures = list(map(
            lambda read_task: executor.submit(read_task.gather_stats, iterations),
            read_tasks
        ))

        futures = read_futures

        for _ in concurrent.futures.as_completed(futures):
            read_data[_.result().ip] = _.result().result

    return read_data


def write(write_task: write_stats_gathering.WriteGatheringTask, iterations: int) -> list:
    logging.info("Start processing write task in pid - {pid}"
                 .format(pid=os.getpid()))

    write_data = write_task.gather_stats(iterations).result
    return write_data


def save_results_to_file(experiment_data, read_data, write_data):
    experiment_results_file = open(default_results_file_name.format(id=experiment_data.experiment_id), "w+")
    experiment_results_file.write(str(experiment_data.experiment_id) + "\n")
    experiment_results_file.write(str(experiment_data.number_of_iterations) + "\n")
    experiment_results_file.write(str(experiment_data.write_delay_ms) + "\n")
    experiment_results_file.write(str(experiment_data.write_consistency_level) + "\n")
    experiment_results_file.write(str(experiment_data.read_consistency_level) + "\n")
    experiment_results_file.write(str(experiment_data.amount_of_instances) + "\n")
    experiment_results_file.write(str(experiment_data.replication_factor) + "\n")
    experiment_results_file.write("READ" + "\n")
    for k, v in read_data.items():
        for kk, vv in v:
            experiment_results_file.write("{ip}:{timestamp}:{version}".format(ip=k, timestamp=kk, version=vv) + "\n")
    experiment_results_file.write("WRITE" + "\n")
    for k, v in write_data:
        experiment_results_file.write(
            "{ip}:{timestamp}:{version}".format(ip=experiment_data.write_ip, timestamp=k, version=v) + "\n")
    experiment_results_file.close()


def main(experiment_data: experiments_data_objects.ExperimentsInputData, chunk_size: int = 5):
    number_of_iterations = experiment_data.number_of_iterations
    read_data = {}
    write_data = []

    logging.info('Submitting stats gathering tasks...')
    table_name = default_table_name.format(id=experiment_data.experiment_id)

    read_task_chunks = list(chunks(
        list(map(lambda ip: read_stats_gathering.ReadGatheringTask(
            consistency_level=consistency_level_name_to_value[experiment_data.read_consistency_level],
            table_name=table_name,
            final_version=experiment_data.number_of_iterations - 1,
            cluster_ip=ip
        ), experiment_data.read_ips)),
        chunk_size))

    logging.info('Total read chunks {size}'.format(size=len(read_task_chunks)))

    write_task = write_stats_gathering.WriteGatheringTask(
        consistency_level=consistency_level_name_to_value[experiment_data.write_consistency_level],
        write_delay_ms=experiment_data.write_delay_ms,
        table_name=table_name,
        node_ip=experiment_data.write_ip
    )

    with Pool(processes=len(read_task_chunks) + 1) as pool:
        read_results_f = [
            pool.apply_async(read_func, (tasks_chunk, number_of_iterations * 20))
            for tasks_chunk in read_task_chunks
        ]
        time.sleep(10)
        write_result_f = pool.apply_async(write, args=(write_task, number_of_iterations))

        read_results = [res.get() for res in read_results_f]
        for res in read_results:
            read_data.update(res)
        write_data = write_result_f.get()

    save_results_to_file(experiment_data, read_data, write_data)
