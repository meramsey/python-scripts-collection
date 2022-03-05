import json
import aiodns
import asyncio
import csv
import os

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)
csvFilePath = os.path.expanduser('~/Downloads/sql_query_results.csv')


async def query(name, query_type):
    return await resolver.query(name, query_type)


def get_hostname_from_ip(ip):
    """Basic get RDNS via PTR lookup.

    :param ip: IP address to lookup
    :type ip: str
    :return: Returns `hostname` if found, or empty string '' otherwise
    :rtype: str
    """
    try:
        reverse_name = ".".join(reversed(ip.split("."))) + ".in-addr.arpa"
        coro = query(reverse_name, "PTR")
        result = loop.run_until_complete(coro)
        return result.name
    except:
        return ""


with open(csvFilePath, mode='r') as infile:
    reader = csv.reader(infile)
    rdns_dict = {rows[0]: rows[1] for rows in reader}
    # removing csv row header 'dedicatedip,domain' from dictionary
    del rdns_dict['dedicatedip']
    # print(rdns_dict)

# # write json
# whmcs_results = os.path.expanduser('~/Downloads/ip_domains_from_whmcs.json')
# with open(whmcs_results, "w") as outfile:
#     json.dump(rdns_dict, outfile)

rdns_dict_rdns_lookups = {}
rdns_to_set = {}
for ip in rdns_dict.keys():
    domain = rdns_dict[ip]
    rdns = get_hostname_from_ip(ip)
    print(f"IP: {ip} "
          f"\nDomain: {domain} "
          f"\nRDNS: {rdns}"
          f"\n======================")
    # print(rdns_dict[ip])
    rdns_dict_rdns_lookups[ip] = {"domain": domain,
                                  "rdns": rdns}

    default_array = ['.static.acmecorp.com', '.static.acme2.com', '.static.acme.com']
    import re
    pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    static_rdns = re.sub(pattern, '', rdns)
    if static_rdns in default_array:
        # print(rdns)
        # print(static_rdns)
        rdns_to_set[ip] = domain
        # print('RDNS that needs set')
        # print(ip, domain)
        # print('=============================')

print('RDNS lookups')
print(rdns_dict_rdns_lookups)
print('=============================')
print('RDNS that needs set')
print(rdns_to_set)

# write json
whmcs_results_rdns_before = os.path.expanduser('~/Downloads/rdns_backfill_after-2.json')
with open(whmcs_results_rdns_before, "w") as outfile:
    json.dump(rdns_dict_rdns_lookups, outfile)

ip_rdns_to_set = os.path.expanduser('~/Downloads/rdns_backfill_to_set_after-2.json')
with open(ip_rdns_to_set, "w") as outfile:
    json.dump(rdns_to_set, outfile)
