import plot_utils

# plot_utils.simple_plot_with_multiple_coordinates(read_stats["206.189.52.16"], write_stats)
# plot_utils.simple_plot_with_multiple_reads(read_stats)
#plot_utils.simple_plot_dict(read_stats["104.248.140.155"])
# plot_utils.simple_plot(write_stats)


def gather_results(experiment_id: int):
    experiment_file_name = 'experiment_{id}_results.txt'.format(id=experiment_id)
    with open(experiment_file_name, "r") as f:
        results = f.read().splitlines()

    read_stats = {}
    write_stats = {}
    read_or_write = ""
    for i in range(7, len(results)):
        line = results[i]
        if line == "READ" or line == "WRITE":
            read_or_write = line
            continue

        arr = line.split(":")
        ip = arr[0]
        timestamp = arr[1]
        version = arr[2]

        if version == '0':
            continue

        if read_or_write == "READ":
            if ip not in read_stats.keys():
                read_stats[ip] = {}

            if version in read_stats[ip].keys():
                pass
            else:
                read_stats[ip][version] = timestamp

        else:
            write_stats[version] = timestamp

    return read_stats, write_stats


def plot_results(exp_name: str, read_r: dict, write_r: dict):

    all_diff = {}

    for ip, data in read_r.items():
        diff = {}

        for version, time in data.items():
            diff[version] = int(time) - int(write_r[version])

        all_diff[ip] = diff

    plot_utils.plot_histogram(exp_name, all_diff)


def plot_results_without_negative(exp_name: str, read_r: dict, write_r: dict):

    all_diff = {}
    dc_diff = {'fra': [], 'sgp': []}
    dc1 = [
        '167.71.48.223',
        '164.90.170.146',
        '164.90.162.132',
        '167.71.51.73',
        '167.172.175.190',
        '164.90.160.153',
        '164.90.170.45',
        '164.90.164.236',
        '167.172.163.152',
        '167.172.163.21',

    ]

    dc2 = [
        '178.128.113.62',
        '178.128.113.141',
        '178.128.126.251',
        '178.128.113.154',
        '178.128.113.31',
        '178.128.113.13',
        '178.128.113.158',
        '178.128.113.167',
        '178.128.113.103',
        '178.128.113.110'
    ]

    for ip, data in read_r.items():
        diff = []

        read_difference = 158 if ip in dc1 else 418
        write_difference = 158

        for version, time in data.items():
            time_diff = int(time) + read_difference - (int(write_r[version]) - write_difference)

            diff.append(time_diff)

        all_diff[ip] = diff

    for k, v in all_diff.items():
        if k in dc1:
            dc_diff['fra'] = dc_diff['fra'] + v
        else:
            dc_diff['sgp'] = dc_diff['sgp'] + v

    plot_utils.density_plot(exp_name, dc_diff)
    # plot_utils.plot_histogram(exp_name, dc_diff)
    # plot_utils.plot_multiple_dict(exp_name, all_diff)




if __name__ == '__main__':

    for i in range(1, 11):
        read_r, write_r = gather_results(i)
        plot_results_without_negative("experiment_{id}".format(id=i), read_r, write_r)








