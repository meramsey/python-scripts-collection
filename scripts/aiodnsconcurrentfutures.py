import concurrent.futures
import timeit
from netaddr import *
import aiodns
import asyncio

ips = [...]
results = []

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)


async def query(name, query_type):
    return await resolver.query(name, query_type)


def get_hostname_from_ip(ip):
    try:
        reverse_name = '.'.join(reversed(ip.split("."))) + ".in-addr.arpa"
        coro = query(reverse_name, 'PTR')
        result = loop.run_until_complete(coro)
        return result.name
    except:
        return ""


with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    results = list(pool.map(get_hostname_from_ip, ips))

print(get_hostname_from_ip('144.202.58.33'))


def main():
    ip_range = IPNetwork('144.202.58.0/22')
    #
    for ip in ip_range:
        #     print(ip)
        print(get_hostname_from_ip(str(ip)))


# main()
elapsed_time = timeit.timeit(main, number=1) / 1
print(elapsed_time)
