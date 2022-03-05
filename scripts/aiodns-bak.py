import datetime
import socket
from socket import getaddrinfo, gethostbyaddr, gethostbyname
import asyncio
import aiodns
import dns
from dns import resolver as dnspythonresolver

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)

async def query(name, query_type):
    return await resolver.query(name, query_type)


# now = datetime.datetime.now()
#
#
#
# # print('Argument List:', str(sys.argv))
# # site = sys.argv[1]
# # dns_server = sys.argv[2]
#
# # Define Domain DNS record Dictionary
# domain_dns_dict = {}
#
#
# domain = "facebook.com"
#
# site = domain
# #myResolver.nameservers = ['1.1.1.1', '8.8.4.4']
# #myResolver.nameservers = ['162.159.25.95', '162.159.24.221']
# print('')
#
# print('DNS Snapshot from '+ str(now.strftime('%Y-%m-%d %H:%M %p')) + ' ' + 'for: ' + site)
# # print('DNS Records for: ' + site)
# #print('')
# print('Whois: https://whois.domaintools.com/' + site)
# print('')
# print('Nameservers:')
# # NS's query the host's DNS
# try:
#     res_ns = loop.run_until_complete(resolver.query(site, 'NS'))
#     # print(res_ns)
#     for elem in res_ns:
#         ns = elem.host
#         ns_ip = socket.gethostbyname(ns)
#         print(ns + " " + ns_ip)
# except:
#         pass
#
# # try:
# #     for elem in resolver.query(site, 'DS'):
# #         print(elem)
# #         ds = str(elem)
# #         print(ds)
# # except KeyError:
# #            pass
#
# print('')
# print('SOA Records:')
# try:
#     # SOA query the host's DNS
#         res_soa = loop.run_until_complete(resolver.query(site, 'SOA'))
#     # for elem in res_soa:
#         print(str(res_soa.nsname) + " " + str(res_soa.hostmaster) + " " + str(res_soa.serial))
# except:
#         pass
#
# print('')
# print('A: IPv4:')
#
# try:
#     # WWW query the host's DNS
#         res_cname = loop.run_until_complete(resolver.query('www.'+ site, 'CNAME'))
#         for elem in res_cname:
#             print('www.'+ site  + ' ==> ' + elem.cname)
# except:
#         pass
#
# try:
#     # WWW query the host's DNS
#         res_www = loop.run_until_complete(resolver.query('www.'+ site, 'A'))
#         for elem in res_www:
#             print('www.'+ site  + ' ==> ' + elem.host)
# except:
#         pass
# try:
#     # A/IPv4 query the host's DNS
#     res_a = loop.run_until_complete(resolver.query(site, 'A'))
#     for elem in res_a:
#         domain_a = elem.host
#         print(domain_a)
# except:
#         pass
#
#
# print('')
# print('AAAA: IPv6:')
# try:
#     # AAAA/IPv6 query the host's DNS
#     res_aaaa = loop.run_until_complete(resolver.query(site, 'AAAA'))
#     for elem in res_aaaa:
#         domain_aaaa = elem.host
#         print(elem.host)
# except:
#         pass
#
#
# print('')
# print('MX Records:')
# try:
#     # MX query the host's DNS
#     res_mx = loop.run_until_complete(resolver.query(site, 'MX'))
#     for elem in res_mx:
#         print(str(elem.host) + ' has preference ' + str(elem.priority))
# except:
#         pass
#
# print('')
# print('TXT Records:')
# # TXT query the host's DNS
# try:
#         res_txt = loop.run_until_complete(resolver.query(site, 'TXT'))
#         for elem in res_txt:
#             print(str(elem.text))
# except:
#             pass
#
# print('')
# print('Domain A Record IP RDNS')
# try:
#     # A/IPv4 query the host's DNS
#     res_a = loop.run_until_complete(resolver.query(site, 'A'))
#     for elem in res_a:
#         domain_a = elem.host
#         #print(domain_a)
#         domain_ptr = socket.gethostbyaddr(elem.host)
#         print(elem.host + ' ==> ' + domain_ptr)
# except:
#         pass
#
# print('')
# print('Domain MX Record IP RDNS')
# try:
#     # MX query the host's DNS
#     res_mx = loop.run_until_complete(resolver.query(site, 'MX'))
#     for elem in res_mx:
#         print(elem.host)
#         for elem.host in elem:
#             res_a = loop.run_until_complete(resolver.query(elem.host, 'A'))
#             print(res_a.host)
#             mxrecord_ip = '144.202.58.32'
#             mxrecord_ptr = socket.gethostbyaddr(mxrecord_ip)
#             print(elem.host + ' ==> ' + mxrecord_ip + ' ==> ' + mxrecord_ptr)
# except:
#         pass

import json


def get_info(obj):
    type_name = type(obj).__name__
    print('Value is of type {}!'.format(type_name))
    prop_names = dir(obj)

    for prop_name in prop_names:
        prop_val = getattr(obj, prop_name)
        prop_val_type_name = type(prop_val).__name__
        print('{} has property "{}" of type "{}"'.format(type_name, prop_name, prop_val_type_name))

        try:
            val_as_str = json.dumps([prop_val], indent=2)[1:-1]
            print('  Here\'s the {} value: {}'.format(prop_name, val_as_str))
        except:
            pass


for rdata in dnspythonresolver.query('dnssec-tools.org', 'DS'):
    print(rdata)
    # get_info(res_dnskey)
    # print(res_dnskey.r)