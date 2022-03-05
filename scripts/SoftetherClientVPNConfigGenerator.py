import itertools
import os
import re
import subprocess
import sys
import requests
import shutil
from shutil import make_archive
from zipfile import ZipFile


# helper functions

def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


def upload_file(file, connection):
    ssh_user, host, path = connection
    destination = f'{ssh_user}@{host}:{path}'
    p = subprocess.Popen(["scp", f'{str(file)}', destination])
    sts = os.waitpid(p.pid, 0)
    print(sts)


def write_config_to_file(content, filepath):
    # Writing to file
    with open(filepath, "w") as file:
        # Writing data to a file
        file.write(content)


def make_archive(source, destination, format='zip'):
    import os
    import shutil
    from shutil import make_archive
    base, name = os.path.split(destination)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    print(f'Source: {source}\nDestination: {destination}\nArchive From: {archive_from}\nArchive To: {archive_to}\n')
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


############### Begin Config ###############################

vpn_servers_dict = dict(
    softy1={"hostname": "softy1.example.com", "ip": "", "country": "NL", "city": "AMSTERDAM"},
    softy3={"hostname": "softy3.example.com", "ip": "", "country": "US", "city": "MIAMI"},
    softy5={"hostname": "softy5.example.com", "ip": "", "country": "US", "city": "New Jersey"},
    softy15={"hostname": "softy15.example.com", "ip": "", "country": "NL", "city": "AMSTERDAM"},
    softy16={"hostname": "softy16.example.com", "ip": "", "country": "CA", "city": "Toronto"})

output_folder_name = os.path.expanduser("~/Desktop/softy_test_generation")

viscosity_profiles_folder_name = 'vpn.wts.com.config_files_visc'
openvpn_profiles_folder_name = 'vpn.wts.com.config_files'
softethervpn_profiles_folder_name = 'SoftEtherVPN_Profiles'

# VPN protocols
protocols = ['udp', 'tcp']

# VPN listener ports
listener_ports = ['443', '992', '1194']

# Typically Signed Cert for VPN server or if self signed
# ca_crt = """
# -----BEGIN CERTIFICATE-----
# SOME BIGASS CERT WOULD HERE
# -----END CERTIFICATE-----
# """

ca_crt = """

"""

# Dummy client cert and key for compatibility

client_cert = """
-----BEGIN CERTIFICATE-----
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
WUlv/XLFpC359g==
-----END CERTIFICATE-----
"""

client_key = """
-----BEGIN PRIVATE KEY-----
MIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQDS6pbnr26ARPnd
+WSy0OS6ZvYcbXKpFCQ1tSvylsYefjqYS2eo9l39QknvKSN8rFycb96Z8idvJ+ie
shiNj3iVaCKPpmFoZpPwIqGiJKYBcoyWuU/5+qP5ngrhxqScmpGIUxrV4L/c27+N
+/y6mjWLGjUcVNntPgY/c6HZGp3TlnP5myCsRY/MFUy4nEMyshnVZcUmsYl/y+FE
hm2Xn5NgOLfHwblWaoCTwu0FEBk8cycSmnmzZmHV2XxK7B2lTs8PffIz1Pf0vLLX
Yw04QaBnD8F2kW4sCTUTAEdXrFLwwyJsPeZfF3gJm6EOq8Emf1CBPqCOWWk9YnRa
Lr2q0edTzsLDjiU8FLOmZZwqWKnoCA0kFAgBIDiQZmmKvqikVJbRuLnE3VRA7rwX
eRnsYvIKUlUmj/EFTsYz/ZeZiOeqtGAN+yi0+fNRE+mCsLehUeM/2MaYuPfawW4B
gFcDXlqWN4hKyaRJOFB9zJd0aj4FPkoZWEUGv7auQ06o2JZ4g3MTbgkGUf+kkISD
fGMQbWQBuomp56uX6Qy02AIpmEBEvhcUSX2PQU/zt5Xvk392o++b1H6OC9Us8OT3
hqS2ahqVYeMjCRZcwNjQKWZrCwamASjIl1B+rCiLywOkycL+SiSATCgNPZBs/Ngg
yfMiooGVjwJYvL+psiiHco7Nxj1dsQIDAQABAoICAFXgZmkXKOrZKtOSg8m6/CZZ
XcPdXF4zcTrc9XPkp+4qfzkbGq3VAhfoMapLGcPdeifH9N7BlgTQPwq+gPjCfdp3
d/r9R5P2kC2qLB2UxnK4bT3BXiruPm2YR939v3B0DuVu0PJcfEI0xx3Mh+6Cc2Kb
3RwYAFN0eZ7EOhXnnHNWQwpSe08pU49I7OAN3954XcRhl5BVoSKDpMj94wllU+BN
t6aB3jCtVITVTSROlbfjOvl8JClDenpT/yOSV8/C8tPf+AnaoMrpOfgwwGUzc1gD
NkZMmIsdhJqj9mhgJbUZ/p4L5gy5xYpD76PFkvNVyzWUhlLvXMY9nBpMBbXTmVfs
/mSUm4pj7t8E2GM3coZCspGAXMG+5oo7EsYX1tGEe6a0EI5Z7TLI9IJ018R2HlTf
Y0tToZx8wcqfxwCmazRo2wUq5G2cOGk0mBlkqqTvu7VIKfI9LFU6vC68KNDLvq2T
9WXjRHNAUlMZyTd2Q8fj6IOB9s8PaYnn/cjaz6icNgD8JqjznffREUU3WCTQ0b6N
cdfnn/+V1KotUvVnPZy+7m+2y3vsNjKvx913zNgaoHKyzj5z2zREWBR+wPWG1Mdj
ybcZHDwiHD9Pj5jFwVAGlAo4U4VtBZmVK3//j67pHul5IIsMjfoUJpvHaTRZAUyj
Z4rH05Btlz8Dg5LR0RgBAoIBAQDvIRzW5LRXyVOIbET+1mRr/3ak7bk6FE/KHDb4
5EJ7kuJX7iI2km+TsPYNkw9ncUbTEjE0D1g9CikaBdZVCIQJcG0LNcP4ZJTWdst2
0F6nyzNiIim/nAIt9KQaMzg4up8T6Rj3dl9gEQlO4ABtsIzR/1M2oeWFkNsPr0xM
SXv7c14lQnZYGUVEHknTPFvFHatIsBeRbw8zHNuplCOtixE7/N56W6LZNTXr3O7s
gw6puLkHiDS6qkQJKl1UfuCECFhELUIWTAbUm/zzV+LLzlcqNciTWeIuY38EvloB
y/ZUYcxN7NH7OiLzkYObPlOHkMpc8D/up84FQOOaH1SaVH4RAoIBAQDhy+zp1Ein
hz/VLCJyEAPiu3noE9ocelrrnRkIm5OWp1gHlJ7nuvru/HBEjgbeseS2opn1t9ia
LKQRLoVAa/XapEdtpn5Vz06N8ksxbA+kI75LcH0uaCQvEkZ8XQBn+vpz1eZUtXfm
2ojAhkhb7AGAb2Os9G/MRjNufiiymBeMbN+rBOlKnO2GkMLiUSWfzsRb0Z1zmCSS
l1EpPP3zvEMo9wiDxYdUZdBGCbF83cimNMM5oaSgjLoD5JObSBA7FpeZWCOd/Obr
bZYLDH7BXj5qif+NLQKj9lY8dJjr9r0e9TfZct+lt/eCa1bvzNWH8sYCGaLE+c7Y
2O/DYY8lp8WhAoIBADOawr2BR4X2VYeITe9s1ukTjUgUYTeucHWeVyKpJ8vBLAVr
x4hdW6TUuJS/WsCpCm68a0/fy9wIWExcXB+noc7jqzSTGsJ8+j26DziJyROO33zb
AIVwJmxCcjORQB3F8FR8pj2pFvYFVyvlXVJOmmUrI4sTrxN+6jddTircZNwjznpd
+GoUsgT8QFRMn0VPnMon7j4daHtQS/sxk+18qHB4po5jPiZ/vC41VH5H3h80VQHS
HAb4fYw4z0FPzCXSIzI7Thq/t22kaBcfrTrsQZVDXBCogg4evKeKaKQgnv0gydU7
OSltJ2PG0E7tSVtlHLanxjQ7lFM/6J43CqvvdfECggEASUIPgKIGXIxOEoy6NEWr
7REkcT6Xomu0OgODTr6jONrcfcEjeU26AnXWuvdVlUUkTnkc+JMIbKUVKhns08Tz
RFfOcO32yUJ0WyuEZ+mGfZu3LuS1SKwzKS6Fve2ypwnP3mtEyrEB0N2QRt6KdYBx
0EjTjxbTevQ/1ZaK/77GzSG5w9PZGQMnMWSgRitLyLieDqhIrGttWj5L79RBFKY9
J/pWQeKBkMljtIWKl1ehtQMjX/xo3EosQ/0SQuwzj+g5kV/+VlDqXvH0H2uTaIt6
NrjFN/mlhKr0ubKettgb7gJjd2KE21B/tkm7MBxGH1COG7pTjBL8oHBqAfsSJYZ0
YQKCAQB9KPikirwQdk/9ErcBoAC8LdwdEH3fA+uZaOPt9Xlwbg5c3zKezlfWq8Xh
sJpPym1a8BQGGeR/g7SLcEuJ8Bjqd4x+XbvFm21wI2VFJQ1qc9zvdkWB2T7iOuXD
idHjaW1WqcXy7RCzl18nvcglQ6UzLO5XOTAEKHqQ5euXNgoOtRWXUZ+F6aCVtfO3
+pMvFSRqMhOPxI0T7N1BUlPIm3TNKdYIlsjnffti5uxEDW/7nv6mx8L+9bromkd7
6dgQVe8brlZg7wkF3z03oY7asVvk9uYEuswh3ypz83NJNy6EK+qv5jQieOKqIoNR
bXQXJZcDGE13qAJownesrS5a6L/r
-----END PRIVATE KEY-----
"""

openvpn_config_template = f"""###############################################################################
# OpenVPN 2.0 Sample Configuration File
# for PacketiX VPN / SoftEther VPN Server
# 
# !!! AUTO-GENERATED BY SOFTETHER VPN SERVER MANAGEMENT TOOL !!!
# 
# !!! YOU HAVE TO REVIEW IT BEFORE USE AND MODIFY IT AS NECESSARY !!!
# 
# This configuration file is auto-generated. You might use this config file
# in order to connect to the PacketiX VPN / SoftEther VPN Server.
# However, before you try it, you should review the descriptions of the file
# to determine the necessity to modify to suitable for your real environment.
# If necessary, you have to modify a little adequately on the file.
# For example, the IP address or the hostname as a destination VPN Server
# should be confirmed.
# 
# Note that to use OpenVPN 2.0, you have to put the certification file of
# the destination VPN Server on the OpenVPN Client computer when you use this
# config file. Please refer the below descriptions carefully.


###############################################################################
# Specify the type of the layer of the VPN connection.
# 
# To connect to the VPN Server as a "Remote-Access VPN Client PC",
#  specify 'dev tun'. (Layer-3 IP Routing Mode)
#
# To connect to the VPN Server as a bridging equipment of "Site-to-Site VPN",
#  specify 'dev tap'. (Layer-2 Ethernet Bridging Mode)

dev tun


###############################################################################
# Specify the underlying protocol beyond the Internet.
# Note that this setting must be correspond with the listening setting on
# the VPN Server.
# 
# Specify either 'proto tcp' or 'proto udp'.

proto udp


###############################################################################
# The destination hostname / IP address, and port number of
# the target VPN Server.
# 
# You have to specify as 'remote <HOSTNAME> <PORT>'. You can also
# specify the IP address instead of the hostname.
# 
# Note that the auto-generated below hostname are a "auto-detected
# IP address" of the VPN Server. You have to confirm the correctness
# beforehand.
# 
# When you want to connect to the VPN Server by using TCP protocol,
# the port number of the destination TCP port should be same as one of
# the available TCP listeners on the VPN Server.
# 
# When you use UDP protocol, the port number must same as the configuration
# setting of "OpenVPN Server Compatible Function" on the VPN Server.

# Note: The below hostname is came from the Dynamic DNS Client function
#       which is running on the VPN Server. If you don't want to use
#       the Dynamic DNS hostname, replace it to either IP address or
#       other domain's hostname.

VPN_SERVER_REMOTES

###############################################################################
# The HTTP/HTTPS proxy setting.
# 
# Only if you have to use the Internet via a proxy, uncomment the below
# two lines and specify the proxy address and the port number.
# In the case of using proxy-authentication, refer the OpenVPN manual.

;http-proxy-retry
;http-proxy [proxy server] [proxy port]


###############################################################################
# The encryption and authentication algorithm.
# 
# Default setting is good. Modify it as you prefer.
# When you specify an unsupported algorithm, the error will occur.
# 
# The supported algorithms are as follows:
#  cipher: [NULL-CIPHER] NULL AES-128-CBC AES-192-CBC AES-256-CBC BF-CBC
#          CAST-CBC CAST5-CBC DES-CBC DES-EDE-CBC DES-EDE3-CBC DESX-CBC
#          RC2-40-CBC RC2-64-CBC RC2-CBC CAMELLIA-128-CBC CAMELLIA-192-CBC CAMELLIA-256-CBC
#  auth:   SHA SHA1 SHA256 SHA384 SHA512 MD5 MD4 RMD160

cipher AES-256-CBC
auth SHA384


###############################################################################
# Other parameters necessary to connect to the VPN Server.
# 
# It is not recommended to modify it unless you have a particular need.
#block-outside-dns
resolv-retry infinite
nobind
persist-key
persist-tun
client
verb 3
auth-user-pass


###############################################################################
# The certificate file of the destination VPN Server.
# 
# The CA certificate file is embedded in the inline format.
# You can replace this CA contents if necessary.
# Please note that if the server certificate is not a self-signed, you have to
# specify the signer's root certificate (CA) here.

<ca>{ca_crt}


</ca>


###############################################################################
# The client certificate file (dummy).
# 
# In some implementations of OpenVPN Client software
# (for example: OpenVPN Client for iOS),
# a pair of client certificate and private key must be included on the
# configuration file due to the limitation of the client.
# So this sample configuration file has a dummy pair of client certificate
# and private key as follows.

<cert>{client_cert}


</cert>

<key>{client_key}

</key>


"""

viscosity_template = """#-- Config Auto Generated By Viscosity --#

#viscosity name VPN_CONNECTION_NAME
#viscosity autoreconnect true
#viscosity dns automatic
#viscosity usepeerdns true
#viscosity manageadapter true
#viscosity startonopen false
VPN_SERVER_REMOTES
dev tun
nobind
persist-key
persist-tun
pull
tls-client
auth-user-pass
ca ca.crt
cert cert.crt
key key.key
cipher AES-256-CBC
auth SHA384
resolv-retry infinite
dev-node {8FA040D2-FDB9-48ED-8C14-FD257DCD22E6}
"""

# Special Note: Auth Type for ldap/radius is "2" if your using basic username and pass you may need to change that
# in the template.

softethervpn_template = """# VPN Client VPN Connection Setting File
# 
# This file is exported using the VPN Client Manager.
# The contents of this file can be edited using a text editor.
# 
# When this file is imported to the Client Connection Manager
#  it can be used immediately.

declare root
{
	bool CheckServerCert false
	uint64 CreateDateTime 0
	uint64 LastConnectDateTime 0
	bool StartupAccount false
	uint64 UpdateDateTime 0

	declare ClientAuth
	{
		uint AuthType 2
		byte EncryptedPassword $
		string Username $
	}
	declare ClientOption
	{
		string AccountName CONNECTION_NAME
		uint AdditionalConnectionInterval 1
		uint ConnectionDisconnectSpan 0
		string DeviceName VPN
		bool DisableQoS false
		bool HalfConnection false
		bool HideNicInfoWindow true
		bool HideStatusWindow false
		string Hostname HOSTNAME_PLACEHOLDER/tcp
		string HubName VPN
		uint MaxConnection 8
		bool NoRoutingTracking false
		bool NoTls1 false
		bool NoUdpAcceleration false
		uint NumRetry 4294967295
		uint Port 443
		uint PortUDP 0
		string ProxyName $
		byte ProxyPassword $
		uint ProxyPort 0
		uint ProxyType 0
		string ProxyUsername $
		bool RequireBridgeRoutingMode false
		bool RequireMonitorMode false
		uint RetryInterval 5
		bool UseCompress false
		bool UseEncrypt true
	}
}
"""


############### END Config ###############################


def generate_multiline_str_from_list(list):
    return "\n".join(list)


def generate_openvpn_remote_combos(server_hosts, listener_ports, protocols):
    # build a list of all remotes for hostname/ip and port/protocol combinations
    list = [server_hosts, listener_ports, protocols]
    combination = [p for p in itertools.product(*list)]
    # print(combination)
    server_remotes = []
    for item in combination:
        host, port, protocol = item
        remote = f"remote {host} {port} {protocol}"
        server_remotes.append(remote)
    return server_remotes


def generate_openvpn_configs(compress=True):
    for server in vpn_servers_dict:
        hostname, ip, country, city = vpn_servers_dict[server].values()
        # print(vpn_servers_dict[server])
        filename = f"{hostname}_{country}_{city}.ovpn"
        print(filename)
        server_hosts = [hostname, ip]
        server_remotes = generate_openvpn_remote_combos(server_hosts, listener_ports, protocols)
        vpn_server_remotes = generate_multiline_str_from_list(server_remotes)
        substitutions = {"VPN_SERVER_REMOTES": vpn_server_remotes}
        content = replace(openvpn_config_template, substitutions)
        ovpn_folder = os.path.join(output_folder_name, openvpn_profiles_folder_name)
        path = os.path.join(ovpn_folder, filename)
        if not os.path.exists(output_folder_name):
            os.makedirs(output_folder_name, exist_ok=True)
        if not os.path.exists(ovpn_folder):
            os.makedirs(ovpn_folder, exist_ok=True)
        write_config_to_file(content, path)
        print(f'VPN Config written: {path}')
        print()
        if compress:
            # Individually ZIP each connection into its own archive
            make_archive(ovpn_folder, str(os.path.join(output_folder_name, f'{ovpn_folder}.zip')))


generate_openvpn_configs()


def generate_viscosity_openvpn_configs(compress=None):
    for server in vpn_servers_dict:
        hostname, ip, country, city = vpn_servers_dict[server].values()
        connection_name = f"{hostname}_{country}_{city}"
        print(connection_name)
        server_hosts = [hostname, ip]
        server_remotes = generate_openvpn_remote_combos(server_hosts, listener_ports, protocols)
        vpn_server_remotes = generate_multiline_str_from_list(server_remotes)
        substitutions = {"VPN_SERVER_REMOTES": vpn_server_remotes, "VPN_CONNECTION_NAME": connection_name}
        content = replace(viscosity_template, substitutions)
        visc_folder = os.path.join(output_folder_name, viscosity_profiles_folder_name)
        config_folder_path = os.path.join(visc_folder, f'{connection_name}.visc')
        paths = [output_folder_name, visc_folder, config_folder_path]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        # connection_name/config.conf
        path = os.path.join(config_folder_path, 'config.conf')
        write_config_to_file(content, path)
        # connection_name/ca.crt
        ca_crt_path = os.path.join(config_folder_path, 'ca.crt')
        write_config_to_file(ca_crt, ca_crt_path)
        # connection_name/cert.crt
        client_cert_path = os.path.join(config_folder_path, 'cert.crt')
        write_config_to_file(content, client_cert_path)
        # connection_name/key.key
        client_key_path = os.path.join(config_folder_path, 'key.key')
        write_config_to_file(content, client_key_path)
        print(f'VPN Config written: {config_folder_path}')
        print()
        if compress == 'single':
            # Individually ZIP each connection into its own archive
            make_archive(config_folder_path, str(f'{config_folder_path}.zip'))
    if compress == 'all':
        # Zip all Viscosity folders into a single ZIP archive
        softethervpn_all_profiles = os.path.join(output_folder_name, viscosity_profiles_folder_name)
        make_archive(softethervpn_all_profiles,
                     str(os.path.join(output_folder_name, f'{viscosity_profiles_folder_name}.zip')))


generate_viscosity_openvpn_configs('all')


def generate_softethervpn_configs(compress=True):
    for server in vpn_servers_dict:
        hostname, ip, country, city = vpn_servers_dict[server].values()
        filename = f"{hostname}_{country}_{city}.vpn"
        print(filename)
        substitutions = {"CONNECTION_NAME": str(filename).replace('.vpn', ''), "HOSTNAME_PLACEHOLDER": hostname}
        content = replace(softethervpn_template, substitutions)
        folder = os.path.join(output_folder_name, softethervpn_profiles_folder_name)
        path = os.path.join(folder, filename)
        if not os.path.exists(output_folder_name):
            os.makedirs(output_folder_name, exist_ok=True)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        write_config_to_file(content, path)
        print(f'VPN Config written: {path}')
        print()
        if compress:
            # Individually ZIP each connection into its own archive
            make_archive(folder, str(os.path.join(output_folder_name, f'{softethervpn_profiles_folder_name}.zip')))


generate_softethervpn_configs()
