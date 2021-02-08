from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy, NeverRetryPolicy
from cassandra.query import tuple_factory
import logging
import commons
import plot_utils
from gathering_result import GatheringResult

logging.basicConfig(level=logging.INFO)


class ReadGatheringTask:

    def __init__(self):
        self.profile = ExecutionProfile(
            load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
            retry_policy=NeverRetryPolicy(),
            consistency_level=ConsistencyLevel.ONE,
            serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
            request_timeout=15,
            row_factory=tuple_factory
        )

        self.cluster = Cluster(port=9044, execution_profiles={EXEC_PROFILE_DEFAULT: self.profile})
        self.session = self.cluster.connect('records', wait_for_all_pools=True)

        logging.info('READ Cluster connection is created')

    def gather_stats(self, number_of_iterations: int) -> GatheringResult:
        results: list = [(0, 0) for _ in range(0, number_of_iterations)]
        logging.info("Start gathering READ results")
        for i in range(0, number_of_iterations):
            version = self.session.execute('SELECT * FROM records.tbl_Records').one()[1]
            results[i] = (commons.current_milli_time_ms(), version)
        logging.info("Finished gathering Read results")

        return GatheringResult("READ", results)


if __name__ == '__main__':
    r = ReadGatheringTask().gather_stats(100)
    plot_utils.simple_plot(r.result)

