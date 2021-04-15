
def process_staleness_distribution(exp_name: str, read_r: dict, write_r: dict, bucket_size_ms: int):
    write_timestamps = list(write_r.values())
    write_timestamps.sort()

    write_data_swapped = {value:key for key, value in write_r.items()}

    buckets = {}
    for idx in range(1, len(write_timestamps)):
        write_1 = int(write_timestamps[idx - 1])
        write_2 = int(write_timestamps[idx])

        version = write_data_swapped[str(write_1)]

        for ip, data in read_r.items():
            buckets[ip] = {}
            for read_version, timestamp in data.items():
                if write_1 < int(timestamp) < write_2:
                    bucket_number = int((int(timestamp) - write_1)/bucket_size_ms)
                    if bucket_number not in buckets[ip]:
                        buckets[ip][bucket_number] = (0, 0)  # stale, non stale
                    if version > read_version:
                        buckets[ip][bucket_number] = (buckets[ip][bucket_number][0] + 1, buckets[ip][bucket_number][1])
                        pass
                    else:
                        buckets[ip][bucket_number] = (buckets[ip][bucket_number][0], buckets[ip][bucket_number][1] + 1)
                        pass
                else:
                    pass
    return buckets
