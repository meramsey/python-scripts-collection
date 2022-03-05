import logging
import sqlite3

import paramiko

target_db = "/home/user/PycharmProjects/WizardAssistantPython/wizardassistant.db"

ssh_id = ''
ssh_priority = ''
ssh_connection_name = ''
ssh_username = ''
ssh_password = ''
ssh_key_passphrase = ''
ssh_public_key = ''
ssh_private_key = ''
ssh_host = ''
ssh_hostname = ''
ssh_port = ''
ssh_proxy_command = ''
ssh_public_key_file = ''
ssh_private_key_file = ''


def default_ssh_connection(priority):
    global ssh_id, ssh_priority, ssh_connection_name, ssh_username, ssh_password, ssh_key_passphrase, ssh_public_key, ssh_private_key, ssh_host, ssh_hostname, ssh_port, ssh_proxy_command, ssh_public_key_file, ssh_private_key_file
    try:
        sqliteConnection = sqlite3.connect(target_db)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from sshconfig where priority = ?"""
        cursor.execute(sqlite_select_query, (priority,))
        print("Reading single row \n")
        record = cursor.fetchone()
        ssh_id = record[0]
        ssh_priority = record[1]
        ssh_connection_name = record[2]
        ssh_username = record[3]
        ssh_password = record[4]
        ssh_key_passphrase = record[5]
        ssh_public_key = record[6]
        ssh_private_key = record[7]
        ssh_host = record[8]
        ssh_hostname = record[9]
        ssh_port = record[10]
        ssh_proxy_command = record[11]
        ssh_public_key_file = record[12]
        ssh_private_key_file = record[13]

        print("Id: ", record[0])
        print("Priority: ", record[1])
        print("Connection Name: ", record[2])
        print("SSH Username: ", record[3])
        print("SSH Password: ", record[4])
        print("SSH KeyPassphrase: ", record[5])
        print("SSH PublicKey: ", record[6])
        print("SSH PrivateKey: ", record[7])
        print("SSH Host: ", record[8])
        print("SSH Hostname: ", record[9])
        print("SSH Port: ", record[10])
        print("SSH ProxyCommand: ", record[11])
        print("SSH PublicKey file: ", record[12])
        print("SSH PrivateKey file: ", record[13])

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read single row from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


default_ssh_connection(0)

print("Id: ", ssh_id)
print("Priority: ", ssh_priority)
print("Connection Name: ", ssh_connection_name)
print("SSH Username: ", ssh_username)
print("SSH Password: ", ssh_password)
print("SSH KeyPassphrase: ", ssh_key_passphrase)
print("SSH PublicKey: ", ssh_public_key)
print("SSH PrivateKey: ", ssh_private_key)
print("SSH Host: ", ssh_host)
print("SSH Hostname: ", ssh_hostname)
print("SSH Port: ", ssh_port)
print("SSH ProxyCommand: ", ssh_proxy_command)
print("SSH PublicKey: ", ssh_public_key_file)
print("SSH PrivateKey: ", ssh_private_key_file)


def get_args(self):
    # hostname = self.get_hostname()
    # port = self.get_port()
    # username = self.get_value('username')
    # password = self.get_argument('password', u'')
    # privatekey, filename = self.get_privatekey()
    # passphrase = self.get_argument('passphrase', u'')
    # totp = self.get_argument('totp', u'')
    global ssh_id, ssh_priority, ssh_connection_name, ssh_username, ssh_password, ssh_key_passphrase, ssh_public_key, ssh_private_key, ssh_host, ssh_hostname, ssh_port, ssh_proxy_command, ssh_public_key_file, ssh_private_key_file
    default_ssh_connection(0)

    hostname_form = self.get_hostname()
    port_form = self.get_port()
    username_form = self.get_value('username')
    password_form = self.get_argument('password', u'')
    privatekey_form, filename = self.get_privatekey()
    passphrase_form = self.get_argument('passphrase', u'')
    totp_form = self.get_argument('totp', u'')

    hostname = ssh_hostname if bool(ssh_hostname) is not False else hostname_form
    port = ssh_port if bool(ssh_port) is not False else port_form
    username = ssh_username if bool(ssh_username) is not False else username_form
    password = ssh_password if bool(ssh_password) is not False else password_form
    privatekey = ssh_private_key if bool(ssh_private_key) is not False else privatekey_form
    passphrase = ssh_key_passphrase if bool(ssh_key_passphrase) is not False else passphrase_form

    if isinstance(self.policy, paramiko.RejectPolicy):
        self.lookup_hostname(hostname, port)

    if privatekey:
        pkey = PrivateKey(privatekey, passphrase, filename).get_pkey_obj()
    else:
        pkey = None

    self.ssh_client.totp = totp
    args = (hostname, port, username, password, pkey)
    logging.debug(args)

    return args


hostname = ssh_hostname if bool(ssh_hostname) is not False else hostname_form
port = ssh_port if bool(ssh_port) is not False else port_form
username = ssh_username if bool(ssh_username) is not False else username_form
password = ssh_password if bool(ssh_password) is not False else password_form
privatekey = ssh_private_key if bool(ssh_private_key) is not False else privatekey_form
passphrase = ssh_key_passphrase if bool(ssh_key_passphrase) is not False else passphrase_form
