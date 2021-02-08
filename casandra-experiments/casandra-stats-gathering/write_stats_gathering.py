import time

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy, NeverRetryPolicy
from cassandra.query import tuple_factory
import logging
import commons
import plot_utils
from gathering_result import GatheringResult

logging.basicConfig(level=logging.INFO)


class WriteGatheringTask:

    def __init__(self):
        self.profile = ExecutionProfile(
            load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
            retry_policy=NeverRetryPolicy(),
            consistency_level=ConsistencyLevel.ONE,
            serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
            request_timeout=15,
            row_factory=tuple_factory
        )

        self.cluster = Cluster(port=9042, execution_profiles={EXEC_PROFILE_DEFAULT: self.profile})
        self.session = self.cluster.connect('records', wait_for_all_pools=True)
        logging.info('WRITE Cluster connection is created')

    def gather_stats(self, number_of_iterations: int) -> GatheringResult:
        results: list = [(0, 0) for _ in range(0, number_of_iterations)]
        logging.info("Start gathering WRITE results")
        for i in range(0, number_of_iterations):
            time.sleep(1)
            self.session.execute(
                """         
                    UPDATE Records.tbl_Records
                    SET version = %s
                    where id = 1
                """, [i])
            results[i] = (commons.current_milli_time_ms(), i)
        logging.info("Finished gathering Write results")

        return GatheringResult("WRITE", results)


if __name__ == '__main__':
    res = WriteGatheringTask().gather_stats(100)
    plot_utils.simple_plot(res.result)
