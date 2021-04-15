import logging
import time
from typing import Optional

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, Session
from cassandra.query import SimpleStatement
from retry import retry

import commons
from experiments_data_objects import GatheringResult

log_format = '[%(levelname)s][%(process)d] %(asctime)s.%(msecs)03d: %(message)s'
logging.basicConfig(
    format=log_format,
    level=logging.INFO,
    datefmt="%H:%M:%S"
)

@retry(tries=3, delay=2)
def connect_cluster(cluster_ip) -> Optional[Session]:
    cluster = Cluster([cluster_ip], connect_timeout=30, control_connection_timeout=10)
    session: Optional[Session] = cluster.connect(wait_for_all_pools=False)
    return session


class WriteGatheringTask:

    def __init__(self,
                 consistency_level: ConsistencyLevel,
                 write_delay_ms: int,
                 table_name: str,
                 node_ip: str):
        self.consistency_level = consistency_level
        self.ip = node_ip
        self.write_delay_s = write_delay_ms / 1000
        self.table_name = table_name
        logging.info('WRITE Cluster connection is created for %s', self.table_name)

    def gather_stats(self, number_of_iterations: int) -> GatheringResult:
        session = connect_cluster(cluster_ip=self.ip)
        results: list = [(0, 0) for _ in range(0, number_of_iterations)]
        logging.info("Start gathering WRITE results into %s", self.table_name)
        for i in range(0, number_of_iterations):
            time.sleep(self.write_delay_s)
            logging.info("Iteration - {i} out of {max}".format(i=i, max=number_of_iterations))
            qry = "UPDATE {table_name} SET version = %s where id = 1".format(table_name=self.table_name)
            query_statement = SimpleStatement(
                qry,
                consistency_level=self.consistency_level
            )
            session.execute(
                query_statement, [i])
            results[i] = (commons.current_time_ms(), i)
        logging.info("Finished gathering Write results from %s", self.table_name)
        session.shutdown()
        return GatheringResult("WRITE", results, self.table_name, self.ip)


