import os
import os.path
import requests
from bs4 import BeautifulSoup

hostname = 'some.hostname.here'  # or localhost if this is running on same server as OLS and it can read password file if decrypted
base_url = f'https://{hostname}:7080'
domain = 'domainToAdd.tld'

admin_pass_file = '/usr/local/lsws/password'
admin_pass = ''  # specify password if its not being read from a password file.

# file looks like this from osclick installer
# WebAdmin username is [admin], password is [$ADMINPASSWORD]."
if os.path.exists(admin_pass_file):
    with open(admin_pass_file, 'r') as file:
        passwd = str(file.read()).replace('WebAdmin username is [admin], password is [', '')
        admin_pass = passwd[:-1]  # this removes the last characters `.` from password file
        admin_pass = admin_pass.replace('].', '')  # this removes the last 1 characters `]` from password file
        print(admin_pass)

# This URL will be the URL that your login form points to with the "action" tag.
POSTLOGINURL = f'{base_url}/login.php'

# This URL is the page you actually want to pull down with requests.
REQUESTURL = f'{base_url}/view/confMgr.php?m=vh'

# This URL is for managing services and restarting
SERVICEMNGRURL = f'{base_url}/view/serviceMgr.php'

login_payload = {
    'userid': 'admin',
    'pass': admin_pass
}

with requests.Session() as session:
    post = session.post(POSTLOGINURL, data=login_payload, verify=False)
    r = session.get(REQUESTURL, verify=False)
    session_text = r.text
    # we need the token value for a hidden input with name tk which looks like `0.22532200 1635712299`
    soup = BeautifulSoup(session_text, 'html.parser')
    soup_inputs = soup.find_all('input', value=True)
    # print(soup_inputs[-1]['value'])
    # we need to make it uri encoded `0.22532200+1635712299`
    token = str(soup_inputs[-1]['value']).replace(' ', '+')
    # print(token)

    url = f'{base_url}/view/confMgr.php?m=vh'

    # Create Vhost config file
    payload1 = f"file_create=configFile&name={domain}&vhRoot=%2Fvar%2Fwww%2F{domain}&configFile=%2Fusr%2Flocal%2Flsws%2Fconf%2Fvhosts%2F{domain}%2Fvhconf.conf&note=&allowSymbolLink=1&enableScript=1&restrained=1&maxKeepAliveReq=&setUIDMode=2&user=&group=&staticReqPerSec=&dynReqPerSec=&outBandwidth=&inBandwidth=&a=s&m=vh&p=top&t=V_TOPD&r=~&tk={token}"
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
    }

    response1 = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=payload1,
                             verify=False)

    # Create Vhost now that file exists
    payload2 = f"name={domain}&vhRoot=%2Fvar%2Fwww%2F{domain}&configFile=%2Fusr%2Flocal%2Flsws%2Fconf%2Fvhosts%2F{domain}%2Fvhconf.conf&note=&allowSymbolLink=1&enableScript=1&restrained=1&maxKeepAliveReq=&setUIDMode=2&user=&group=&staticReqPerSec=&dynReqPerSec=&outBandwidth=&inBandwidth=&a=s&m=vh&p=top&t=V_TOPD&r=~&tk={token}"
    response2 = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=payload2,
                             verify=False)

    # Add to default listener
    url = f'{base_url}/view/confMgr.php'
    payload_defaultlistener = f'vhost={domain}&domain={domain}&a=s&m=sl_Default&p=lg&t=L_VHMAP&r=Default%60~&tk={token}'
    response3 = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data=payload_defaultlistener,
                             verify=False)

    # Add to defaultSSL listener
    payload_default_ssl_listener = f'vhost={domain}&domain={domain}&a=s&m=sl_Defaultssl&p=lg&t=L_VHMAP&r=Defaultssl%60~&tk={token}'
    response4 = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data=payload_default_ssl_listener,
                             verify=False)

    # Setup General > General options
    payload_general_general = f'docRoot=%24VH_ROOT%2Fhtml&vhDomain=%24VH_DOMAIN&vhAliases=www.%24VH_DOMAIN&adminEmails=admin%40%24VH_DOMAIN&enableGzip=1&enableBr=1&enableIpGeo=&cgroups=&a=s&m=vh_{domain}&p=g&t=V_GENERAL&r=&tk={token}'
    response_general_general = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                            data=payload_general_general,
                                            verify=False)

    # Setup General > Index Files
    payload_general_index = f'useServer=0&indexFiles=index.php%2C+index.html&autoIndex=&autoIndexURI=&a=s&m=vh_{domain}&p=g&t=VT_INDXF&r=&tk={token}'
    response_general_index = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                          data=payload_general_index,
                                          verify=False)

    # Setup General > php.ini Override
    payload_general_phpini = f'data=php_admin_flag+log_errors+On%0D%0Aphp_admin_value+error_log+logs%2Fphp_error_log&a=s&m=vh_{domain}&p=g&t=VT_PHPINIOVERRIDE&r=&tk={token}'
    response_general_phpini = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                           data=payload_general_phpini,
                                           verify=False)

    # Setup Log > Virtual Host Log
    payload_log_vhostlog = f'useServer=0&fileName=%24VH_ROOT%2Fhtml%2Flogs%2F{domain}.error_log&logLevel=ERROR&rollingSize=10M&keepDays=&compressArchive=&a=s&m=vh_{domain}&p=log&t=V_LOG&r=&tk={token}'
    response_log_vhostlog = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_log_vhostlog,
                                         verify=False)

    # Setup Log > Access Log
    payload_log_vhost_acccesslog = f'useServer=0&fileName=%24VH_ROOT%2Fhtml%2Flogs%2F{domain}.access_log&pipedLogger=&logFormat=%22%25h+%25l+%25u+%25t+%22%25r%22+%25%3Es+%25b+%22%25%7BReferer%7Di%22+%22%25%7BUser-Agent%7Di%22%22&logHeaders1=1&logHeaders2=2&logHeaders4=4&rollingSize=10M&keepDays=10&compressArchive=&bytesLog=&a=s&m=vh_{domain}&p=log&t=V_ACLOG&r=~&tk={token}'
    response_log_vhost_acccesslog = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                 data=payload_log_vhost_acccesslog,
                                                 verify=False)

    payload_realm_first = f'a=a&m=vh_{domain}&p=sec&t=V_REALM_FILE&r=~&tk={token}'
    response_realm_first = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                        data=payload_realm_first,
                                        verify=False)

    # these have to be created before realm or it fails
    # Create htpasswd/htgroup files
    payload_htpasswd = f'file_create=userDB%3Alocation&name=Default&note=&userDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F%24VH_NAME%2Fhtpasswd&userDB%3AmaxCacheSize=&userDB%3AcacheTimeout=&groupDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F%24VH_NAME%2Fhtgroup&groupDB%3AmaxCacheSize=&groupDB%3AcacheTimeout=&a=s&m=vh_{domain}&p=sec&t=V_REALM_FILE&r=~&tk={token}'
    payload_htgroup = f'file_create=groupDB%3Alocation&name=Default&note=&userDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F%24VH_NAME%2Fhtpasswd&userDB%3AmaxCacheSize=&userDB%3AcacheTimeout=&groupDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F%24VH_NAME%2Fhtgroup&groupDB%3AmaxCacheSize=&groupDB%3AcacheTimeout=&a=s&m=vh_{domain}&p=sec&t=V_REALM_FILE&r=~&tk={token}'

    response_htpasswd = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=payload_htpasswd,
                                     verify=False)
    response_htgroup = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                    data=payload_htgroup,
                                    verify=False)

    # Setup Security > Realm
    payload_realm = f'name=Default&note=Default+password+protected+realm&userDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F{domain}%2Fhtpasswd&userDB%3AmaxCacheSize=&userDB%3AcacheTimeout=&groupDB%3Alocation=%24SERVER_ROOT%2Fconf%2Fvhosts%2F{domain}%2Fhtgroup&groupDB%3AmaxCacheSize=&groupDB%3AcacheTimeout=&a=s&m=vh_{domain}&p=sec&t=V_REALM_FILE&r=~&tk={token}'
    response_realm = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                  data=payload_realm,
                                  verify=False)

    # External App > External Applications
    phpver = 'lsphp74'
    payload_external_app = f'name={phpver}&address=uds%3A%2F%2Ftmp%2Flshttpd%2F{domain}.sock&note=&maxConns=35&env=PHP_LSAPI_CHILDREN%3D35%0D%0APHP_INI_SCAN_DIR%3D%3A%24VH_ROOT%2Fhtml&initTimeout=600&retryTimeout=0&persistConn=1&pcKeepAliveTimeout=&respBuffer=0&autoStart=2&path=%2Fusr%2Flocal%2Flsws%2F{phpver}%2Fbin%2Flsphp&backlog=100&instances=1&extUser=&extGroup=&umask=&runOnStartUp=3&extMaxIdleTime=&priority=0&memSoftLimit=2047M&memHardLimit=2047M&procSoftLimit=400&procHardLimit=500&a=s&m=vh_{domain}&p=ext&t=A_EXT_LSAPI&r=~&tk={token}'
    response_external_app = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_external_app,
                                         verify=False)

    # Script Handler > Script Handler Definition
    payload_script_handler = f'suffix=php&type=lsapi&handler={phpver}&note=&a=s&m=vh_{domain}&p=sh&t=A_SCRIPT&r=~&tk={token}'
    response_script_handler = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                           data=payload_script_handler,
                                           verify=False)

    # Rewrite > Rewrite Control
    payload_rewrite_control = f'enable=1&autoLoadHtaccess=1&logLevel=0&a=s&m=vh_{domain}&p=rw&t=VT_REWRITE_CTRL&r=&tk={token}'
    response_rewrite_control = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                            data=payload_rewrite_control,
                                            verify=False)

    # Context > deny public access to logs/
    payload_context_deny_logs = f'uri=%2Flogs%2F&location=logs%2F&allowBrowse=0&note=Deny+public+access+to+logs+directory&enableExpires=&expiresDefault=&expiresByType=&extraHeaders=&addMIMEType=&forceType=&defaultType=&indexFiles=&autoIndex=&realm=&authName=&required=&accessControl%3Aallow=&accessControl%3Adeny=&authorizer=&rewrite%3Aenable=&rewrite%3Ainherit=&rewrite%3Abase=&rewrite%3Arules=&addDefaultCharset=off&defaultCharsetCustomized=&enableIpGeo=&phpIniOverride%3Adata=&a=s&m=vh_{domain}&p=ctx&t=VT_CTXG&r=~&tk={token}'
    response_context_deny_logs = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                              data=payload_context_deny_logs,
                                              verify=False)

    # Context > default headers/rewrites for / context
    payload_context_base = f'uri=%2F&location=&allowBrowse=1&note=Default+Context+Headers&enableExpires=&expiresDefault=&expiresByType=&extraHeaders=X-Frame-Options+%22SAMEORIGIN%22+always%0D%0AX-XSS-Protection+%221%3B+mode%3Dblock%22+always%3B&addMIMEType=&forceType=&defaultType=&indexFiles=&autoIndex=&realm=&authName=&required=&accessControl%3Aallow=&accessControl%3Adeny=&authorizer=&rewrite%3Aenable=1&rewrite%3Ainherit=&rewrite%3Abase=&rewrite%3Arules=&addDefaultCharset=off&defaultCharsetCustomized=&enableIpGeo=&phpIniOverride%3Adata=&a=s&m=vh_{domain}&p=ctx&t=VT_CTXG&r=~&tk={token}'
    response_context_base = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_context_base,
                                         verify=False)

    # SSL > SSL Private Key & Certificate
    payload_ssl_keys = f'keyFile=%2Fetc%2Fletsencrypt%2Flive%2F{domain}%2Fprivkey.pem&certFile=%2Fetc%2Fletsencrypt%2Flive%2F{domain}%2Ffullchain.pem&certChain=1&CACertPath=&CACertFile=&a=s&m=vh_{domain}&p=vhssl&t=LVT_SSL_CERT&r=&tk={token}'
    response_ssl_keys = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data=payload_ssl_keys,
                                     verify=False)

    # SSL > SSL Protocol
    payload_ssl_protocol = f'ciphers=EECDH%2BAESGCM%3AEDH%2BAESGCM%3AAES256%2BEECDH%3AAES256%2BEDH%3AECDHE-RSA-AES128-GCM-SHA384%3AECDHE-RSA-AES128-GCM-SHA256%3AECDHE-RSA-AES128-GCM-SHA128%3ADHE-RSA-AES128-GCM-SHA384%3ADHE-RSA-AES128-GCM-SHA256%3ADHE-RSA-AES128-GCM-SHA128%3AECDHE-RSA-AES128-SHA384%3AECDHE-RSA-AES128-SHA128%3AECDHE-RSA-AES128-SHA%3AECDHE-RSA-AES128-SHA%3ADHE-RSA-AES128-SHA128%3ADHE-RSA-AES128-SHA128%3ADHE-RSA-AES128-SHA%3ADHE-RSA-AES128-SHA%3AECDHE-RSA-DES-CBC3-SHA%3AEDH-RSA-DES-CBC3-SHA%3AAES128-GCM-SHA384%3AAES128-GCM-SHA128%3AAES128-SHA128%3AAES128-SHA128%3AAES128-SHA%3AAES128-SHA%3ADES-CBC3-SHA%3AHIGH%3A\u0021aNULL%3A\u0021eNULL%3A\u0021EXPORT%3A\u0021DES%3A\u0021MD5%3A\u0021PSK%3A\u0021RC4&enableECDHE=1&enableDHE=&DHParam=&a=s&m=vh_{domain}&p=vhssl&t=VT_SSL&r=&tk={token}'
    response_ssl_protocol = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_ssl_protocol,
                                         verify=False)

    # SSL > Security
    payload_ssl_security = f'renegProtection=1&sslSessionCache=1&sslSessionTickets=&enableSpdy1=1&enableSpdy2=2&enableSpdy4=4&enableSpdy8=8&enableQuic=1&a=s&m=vh_{domain}&p=vhssl&t=VT_SSL_FEATURE&r=&tk={token}'
    response_ssl_security = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_ssl_security,
                                         verify=False)

    # SSL > OCSP Stapling
    payload_ssl_stapling = f'enableStapling=1&ocspRespMaxAge=86400&ocspResponder=&ocspCACerts=&a=s&m=vh_{domain}&p=vhssl&t=LVT_SSL_OCSP&r=&tk={token}'
    response_ssl_stapling = session.post(url=url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data=payload_ssl_stapling,
                                         verify=False)

    # SSL > Client Verification
    payload_ssl_client_verification = f'clientVerify=0&verifyDepth=&crlPath=&crlFile=&a=s&m=vh_{domain}&p=vhssl&t=LVT_SSL_CLVERIFY&r=&tk={token}'
    response_ssl_client_verification = session.post(url=url,
                                                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                    data=payload_ssl_client_verification,
                                                    verify=False)

    # Restart service gracefully so config is loaded
    restart_payload = {
        'act': 'restart'
    }
    r = session.post(SERVICEMNGRURL, data=restart_payload, verify=False)
    print(r.text)
