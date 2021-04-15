from tcp_latency import measure_latency
from multiprocessing import Pool
import csv
import concurrent.futures

hosts_dc_fra = [
    '167.71.48.223',
    '164.90.170.146',
    '164.90.162.132',
    '167.71.51.73',
    '167.172.175.190',
    '164.90.160.153',
    '164.90.170.45',
    '164.90.164.236',
    '167.172.163.152',
    '167.172.163.21'
]

hosts_dc_sgp = [
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


def measure(host_ips: list) -> dict:
    ip_map = {}
    for host_ip in host_ips:
        print('Start Measuring for {ip}\n'.format(ip=host_ip))
        measured_latencies = measure_latency(host=host_ip, port=9042, runs=300, timeout=1)
        print('Finished Measuring for {ip}'.format(ip=host_ip))
        print(measured_latencies)
        ip_map[host_ip] = measured_latencies[1:]
        # Because first call is always slower than the rest. (Caching, memorization, etc.)
    return ip_map


def split_list(a_list):
    half = len(a_list)//2
    return a_list[:half], a_list[half:]


def measure_in_threads(host_ips: list) -> dict:
    ip_list1, ip_list2 = split_list(host_ips)
    data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(measure, ip_list1)
        f2 = executor.submit(measure, ip_list2)

        for _ in concurrent.futures.as_completed([f1, f2]):
            data.update(_.result())
    return data


if __name__ == '__main__':
    all_hosts = [hosts_dc_fra, hosts_dc_sgp]
    with Pool(2) as p:
        results = p.map(measure_in_threads, all_hosts)

    with open('ip_latencies.csv', mode='w') as csv_file:
        fieldnames = ['ip', 'latency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for result in results:
            for ip, latencies in result.items():
                for latency in latencies:
                    writer.writerow({'ip': ip, 'latency': latency})
