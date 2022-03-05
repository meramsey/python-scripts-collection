import datetime
import socket
import timeit
from socket import getaddrinfo
import dns
from dns import reversename, resolver
import asyncio
import aiodns
import whois

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)


async def query(name, query_type):
    return await resolver.query(name, query_type)


coro = query('google.com', 'A')
result = loop.run_until_complete(coro)

domain = 'wizardassistant.com'
site = domain

# res_cname = loop.run_until_complete(resolver.query(domain, 'CNAME'))
# res_a = loop.run_until_complete(resolver.query(domain, 'A'))
# res_aaaa = loop.run_until_complete(resolver.query(domain, 'AAAA'))
# res_soa = loop.run_until_complete(resolver.query(domain, 'SOA'))
# res_ns = loop.run_until_complete(resolver.query(domain, 'NS'))
# res_mx = loop.run_until_complete(resolver.query(domain, 'MX'))
# res_txt = loop.run_until_complete(resolver.query(domain, 'TXT'))
# res_ptr = loop.run_until_complete(resolver.query(domain, 'PTR'))


now = datetime.datetime.now()


def dns_lookup():
    global domain, url, email, email2, username, clientip, date_time_input
    # domain = self.domaininput.text().lower()
    # self.form_variable_setup()
    # Clear current box contents
    # self.dns_clear()
    # Registrar whois lookups
    try:
        domainwhois = whois.query(domain)
        # self.dnstableWidget.append('Registrar Information: ' + domain)
        # self.dnstableWidget.append('Registrar: ' + str(domainwhois.registrar))
        # self.dnstableWidget.append('Status: ' + str(domainwhois.status))
        # self.dnstableWidget.append('Last Updated: ' + str(domainwhois.last_updated))
        # self.dnstableWidget.append('Expiration: ' + str(domainwhois.expiration_date))
        # self.dnstableWidget.append(str(domainwhois.__dict__))
        # self.WhoisUrl.setText('https://whois.domaintools.com/' + domain)
        # self.RegistrarValue.setText(str(domainwhois.registrar))
        # self.RegistrarStatusValue.setText(str(domainwhois.status.rsplit(" ")[0]))
        # self.DomainExpiresValue.setText(str(domainwhois.expiration_date))

    except:
        Exception
    # self.dnstableWidget.append('Unsupported Domain extension')
    pass

    # self.dnstableWidget.append('')
    # DNS Lookups
    site = domain

    loop = asyncio.get_event_loop()
    resolver = aiodns.DNSResolver(loop=loop)

    async def query(name, query_type):
        return await resolver.query(name, query_type)

    dnspythonresolver = dns.resolver.Resolver()
    dnspythonresolver.nameservers = ['1.1.1.1', '8.8.4.4', "1.0.0.1", "8.8.8.8", ]
    dnspythonresolver.timeout = 2
    dnspythonresolver.lifetime = 2
    # myResolver.nameservers = ['162.159.25.95', '162.159.24.221']
    # self.dnstableWidget.append('')

    now = datetime.datetime.now()

    # myResolver.nameservers = ['1.1.1.1', '8.8.4.4']
    # myResolver.nameservers = ['162.159.25.95', '162.159.24.221']
    print('')

    print('DNS Snapshot from ' + str(now.strftime('%Y-%m-%d %H:%M %p')) + ' ' + 'for: ' + str(site))
    # print('DNS Records for: ' + site)
    # print('')
    print('Whois: https://whois.domaintools.com/' + str(site))
    print('')
    print('Nameservers:')
    # self.dnstableWidget.append(
    #   'DNS Snapshot from ' + str(now.strftime('%Y-%m-%d %H:%M %p')) + ' ' + 'for: ' + str(site))
    # self.dnstableWidget.append('Whois: https://whois.domaintools.com/' + site)
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('Nameservers:')
    # NS's query the host's DNS
    try:
        res_ns = loop.run_until_complete(resolver.query(site, 'NS'))
        # print(res_ns)
        for elem in res_ns:
            ns = elem.host
            ns_ip = socket.gethostbyname(ns)
            print(ns + " " + ns_ip)
            # self.dnstableWidget.append(ns + ' ' + ns_ip)
            if "cloudflare" in elem.host:
                print("FullZone detected")
                # self.CloudflareStatus.setText("FullZone detected")
                # self.CloudflareStatus.setStyleSheet("QLabel { background-color : red}")
    except:
        pass

    # try:
    #     for elem in resolver.query(site, 'DS'):
    #         print(elem)
    #         ds = str(elem)
    #         print(ds)
    # except KeyError:
    #            pass

    print('')
    print('SOA Records:')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('SOA Records:')
    try:
        # SOA query the host's DNS
        res_soa = loop.run_until_complete(resolver.query(site, 'SOA'))
        # for elem in res_soa:
        print(str(res_soa.nsname) + " " + str(res_soa.hostmaster) + " " + str(res_soa.serial))
        # self.dnstableWidget.append(str(res_soa.nsname) + " " + str(res_soa.hostmaster) + " " + str(res_soa.serial))
        # self.DNSSOAValue.setText(str(res_soa.nsname))
        if "cloudflare" in res_soa.nsname:
            print("FullZone detected")
            # self.CloudflareStatus.setText("FullZone detected")
            # self.CloudflareStatus.setStyleSheet("QLabel { background-color : red}")
    except:
        pass

    print('')
    print('A: IPv4:')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('A: IPv4:')
    try:
        # WWW query the host's DNS
        res_cname = loop.run_until_complete(resolver.query('www.' + site, 'CNAME'))
        for elem in res_cname:
            print('www.' + site + ' ==> ' + elem.cname)
            # self.dnstableWidget.append('www.' + site + ' ==> ' + elem.cname)
            if "cloudflare" in elem.cname:
                print("CNAME detected")
                # self.CloudflareStatus.setText("CNAME detected")
                # self.CloudflareStatus.setStyleSheet("QLabel { background-color : red}")
    except:
        pass

    try:
        # WWW query the host's DNS
        res_www = loop.run_until_complete(resolver.query('www.' + site, 'A'))
        for elem in res_www:
            print('www.' + site + ' ==> ' + elem.host)
            # self.dnstableWidget.append('www.' + site + ' ==> ' + elem.host)
    except:
        pass
    try:
        # A/IPv4 query the host's DNS
        res_a = loop.run_until_complete(resolver.query(site, 'A'))
        for elem in res_a:
            domain_a = elem.host
            # print(elem.host)
            addr = reversename.from_address(elem.host)
            # print(addr)
            domain_ptr = dnspythonresolver(addr, "PTR")[0]
            print(str(domain_ptr))
            # domain_ptr = loop.run_until_complete(resolver.query(str(addr), 'PTR'))[0]
            # domain_ptr = socket.gethostbyaddr(str(rdata))[0]
            # self.DomainIPvalue.setText(domain_a)
            # print(domain_a + ' ==> ' + domain_ptr)
            # self.dnstableWidget.append(domain_a)
    except:
        pass

    print('')
    print('AAAA: IPv6:')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('AAAA: IPv6:')
    try:
        # AAAA/IPv6 query the host's DNS
        res_aaaa = loop.run_until_complete(resolver.query(site, 'AAAA'))
        for elem in res_aaaa:
            domain_aaaa = elem.host
            print(domain_aaaa)
            # self.dnstableWidget.append(domain_aaaa)
    except:
        pass

    print('')
    print('MX Records:')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('MX Records:')
    try:
        # MX query the host's DNS
        res_mx = loop.run_until_complete(resolver.query(site, 'MX'))
        for elem in res_mx:
            print(str(elem.host) + ' has preference ' + str(elem.priority))
            # self.dnstableWidget.append(str(elem.host) + ' has preference ' + str(elem.priority))
    except:
        pass

    print('')
    print('TXT Records:')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('TXT Records:')
    # TXT query the host's DNS
    try:
        res_txt = loop.run_until_complete(resolver.query(site, 'TXT'))
        for elem in res_txt:
            print(str(elem.text))
            # self.dnstableWidget.append(str(elem.text))
    except:
        pass

    print('')
    print('Domain A Record IP RDNS')
    # self.dnstableWidget.append('')
    # self.dnstableWidget.append('Domain A Record IP RDNS')

    try:
        for rdata in dnspythonresolver.query(site, 'A'):
            # print(rdata)
            domain_ptr = socket.gethostbyaddr(str(rdata))[0]
            # self.HostnameValue.setText(str(domain_ptr))
            # print(domain_ptr)
            print(str(rdata) + ' ==> ' + domain_ptr)
        # self.dnstableWidget.append(str(rdata) + ' ==> ' + str(domain_ptr))
    except socket.herror:
        pass

    try:
        for rdata in dnspythonresolver.query('www.' + site, 'A'):
            # print(rdata)
            domain_www2 = str(rdata)
            print('www.' + site + ' ' + '===>' + ' ' + domain_www2)
            # self.dnstableWidget.append('www.' + site + ' ' + '===>' + ' ' + domain_www2)
    except dns.resolver.NoAnswer:
        print('www.' + site + 'not found')
        # self.dnstableWidget.append('www.' + site + 'not found')
    except AttributeError:
        print("'CNAME' object has no attribute 'answer'")
        # self.dnstableWidget.append("'CNAME' object has no attribute 'answer'")

    # self.dnstableWidget.append('')
    print('MX Record  ==> IP  ==> RDNs/Ptr')
    # self.dnstableWidget.append('MX Record  ==> IP  ==> RDNs/Ptr')

    try:
        for rdata in dnspythonresolver.query(site, 'MX'):
            # print(rdata)
            mxrecord = getattr(rdata, 'exchange')
            mxrecord = str(mxrecord).rstrip('.')
            mxrecord = mxrecord.rstrip('.')
            # print(mxrecord)
            mxrecord_ip = socket.gethostbyname(mxrecord)
            mxrecord_ptr = socket.gethostbyaddr(mxrecord_ip)[0]
            # print(mxrecord_ptr)
            print(mxrecord + ' ==> ' + mxrecord_ip + ' ==> ' + mxrecord_ptr)
            # self.dnstableWidget.append(str(mxrecord) + ' ==> ' + str(mxrecord_ip) + ' ==> ' + str(mxrecord_ptr))
    except socket.herror:
        pass
    try:
        # DNSSec checks
        for rdata in dnspythonresolver.query(site, 'DS'):
            print(rdata)
            if bool(rdata) is not False:
                print('DNSSEC DS Found')
                # self.DNSSECValue.setText('DNSSEC DS Found')
                # self.DNSSECValue.setStyleSheet("QLabel { background-color : red}")
    except:
        pass
    print('============================================')


elapsed_time = timeit.timeit(dns_lookup, number=1) / 1
print(elapsed_time)
