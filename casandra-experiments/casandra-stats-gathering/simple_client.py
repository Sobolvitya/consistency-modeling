from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy, NeverRetryPolicy
from cassandra.query import tuple_factory

if __name__ == "__main__":
    profile = ExecutionProfile(
        load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
        retry_policy=NeverRetryPolicy(),
        consistency_level=ConsistencyLevel.ONE,
        serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
        request_timeout=15,
        row_factory=tuple_factory
    )

    cluster = Cluster(port=9042, execution_profiles={EXEC_PROFILE_DEFAULT: profile})
    session = cluster.connect('records', wait_for_all_pools=True)
    rows = session.execute('SELECT * FROM records.tbl_Records')
    for row in rows:
        print(row[0])

