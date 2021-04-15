import logging

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
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
def connect_cluster(cluster_ip):
    cluster = Cluster([cluster_ip], connect_timeout=30, control_connection_timeout=10)
    session = cluster.connect(wait_for_all_pools=False)
    return session


class ReadGatheringTask:

    def __init__(self,
                 final_version: int,
                 consistency_level: ConsistencyLevel,
                 table_name: str,
                 cluster_ip: str):

        self.final_version = final_version
        self.ip = cluster_ip
        self.consistency_level = consistency_level
        self.table_name = table_name
        logging.info('READ Cluster connection is created for %s', self.table_name)

    def gather_stats(self, number_of_iterations: int) -> GatheringResult:
        results: list = [(0, 0) for _ in range(0, number_of_iterations)]
        try:
            session = connect_cluster(cluster_ip=self.ip)
            logging.info("Start gathering READ results from %s", self.table_name)
            for i in range(0, number_of_iterations):
                qry = "SELECT * FROM {table_name}".format(table_name=self.table_name)
                query_statement = SimpleStatement(
                    qry,
                    consistency_level=self.consistency_level
                )
                time_start = commons.current_time_ms()
                version = session.execute(query_statement).one()[1]
                results[i] = (time_start, version)

                if version == self.final_version:
                    logging.info("Finished gathering Read results from %s", self.table_name)
                    return GatheringResult("READ", results[:i + 1], self.table_name, self.ip)

            logging.info("Finished gathering Read results from %s", self.table_name)
            session.shutdown()
        except Exception as e:
            logging.error(f"[{self.ip}] Exception occurred during execution{e.__str__()}")

        return GatheringResult("READ", results, self.table_name, self.ip)

