"""
    Stores results after stats gathering
    result field stores data in a map format - (timestamp, version_of_update)
"""


class GatheringResult:
    def __init__(self,
                 gathering_type: str,
                 result: list,
                 table_name: str,
                 ip: str):
        self.gathering_type = gathering_type
        self.result = result
        self.table_name = table_name
        self.ip = ip


"""
    Stores data which is needed for the experiment run
"""


class ExperimentsInputData:
    def __init__(self,
                 experiment_id: int,
                 amount_of_instances: int,
                 replication_factor: int,
                 read_consistency_level: str,  # according to numbers from ConsistencyLevel.name_to_value
                 write_consistency_level: str,  # according to numbers from ConsistencyLevel.name_to_value
                 write_delay_ms: int,
                 number_of_iterations: int,
                 write_ip: str,
                 read_ips: list
                 ):
        self.experiment_id = experiment_id
        self.amount_of_instances = amount_of_instances
        self.replication_factor = replication_factor
        self.read_consistency_level = read_consistency_level
        self.write_consistency_level = write_consistency_level
        self.write_delay_ms = write_delay_ms
        self.number_of_iterations = number_of_iterations
        self.write_ip = write_ip
        self.read_ips = read_ips
