import read_stats_gathering
import write_stats_gathering
import plot_utils
import logging
import concurrent.futures

log_format = '%(asctime)s: %(message)s'
logging.basicConfig(
    format=log_format,
    level=logging.DEBUG,
    datefmt="%H:%M:%S"
)


def main():
    number_of_iterations = 20
    read_data = []
    write_data = []
    logging.info('Submitting stats gathering tasks...')
    read_task = read_stats_gathering.ReadGatheringTask()
    write_task = write_stats_gathering.WriteGatheringTask()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        read_future = executor.submit(read_task.gather_stats, number_of_iterations * 300)
        write_future = executor.submit(write_task.gather_stats, number_of_iterations)
        for _ in concurrent.futures.as_completed([read_future, write_future]):
            if _.result().gathering_type == "READ":
                read_data = _.result().result
            else:
                write_data = _.result().result
        executor.shutdown()

    plot_utils.simple_plot_with_multiple_coordinates(read_data, write_data)


if __name__ == '__main__':
    main()

