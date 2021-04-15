import time

import threadedprocess as threadedprocess

import read_stats_gathering
import write_stats_gathering
import plot_utils
import logging
import concurrent.futures
import experiments_data_objects
from cassandra import ConsistencyLevel
import multiprocessing
from multiprocessing import Pool

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


def main(experiment_data: experiments_data_objects.ExperimentsInputData, debug: bool = False):
    number_of_iterations = experiment_data.number_of_iterations
    read_data = {}
    write_data = []

    logging.info('Submitting stats gathering tasks...')
    table_name = default_table_name.format(id=experiment_data.experiment_id)

    read_tasks = list(map(lambda ip: read_stats_gathering.ReadGatheringTask(
        consistency_level=consistency_level_name_to_value[experiment_data.read_consistency_level],
        table_name=table_name,
        final_version=experiment_data.number_of_iterations - 1,
        cluster_ip=ip
    ), experiment_data.read_ips))

    logging.info('Total read chunks {size}'.format(size=len(read_tasks)))

    write_task = write_stats_gathering.WriteGatheringTask(
        consistency_level=consistency_level_name_to_value[experiment_data.write_consistency_level],
        write_delay_ms=experiment_data.write_delay_ms,
        table_name=table_name,
        node_ip=experiment_data.write_ip
    )

    with threadedprocess.ThreadedProcessPoolExecutor(max_processes=5, max_threads=5) as executor:
        read_futures = list(map(
            lambda read_task: executor.submit(read_task.gather_stats, number_of_iterations * 20),
            read_tasks
        ))

        write_future = executor.submit(write_task.gather_stats, number_of_iterations)
        futures = read_futures
        futures.append(write_future)

        for _ in concurrent.futures.as_completed(futures):
            if _.result().gathering_type == "READ":
                read_data[_.result().ip] = _.result().result
            else:
                write_data = _.result().result
        executor.shutdown()

    for task in read_tasks:
        task.close()
    write_task.close()

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
    # if debug:
    #     plot_utils.simple_plot_with_multiple_coordinates(read_data, write_data)
