#!/usr/bin/python3
"""
Capture Ruggedcom device configurations. Used by CA Spectrum NCM.
"""

import argparse
from time import sleep

import paramiko

parser = argparse.ArgumentParser(description='Capture RuggedCom configurations')
parser.add_argument('host', type=str, help='Device ip address')
parser.add_argument('username', type=str, help='Username for connecting')
parser.add_argument('password', type=str, help='Passwrod for connecting')
# CA Spectrum send extra, unnecessary arguments
parser.add_argument('dummy', type=str, nargs="*", help='Extra discarded arguments')

args = parser.parse_args()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# TODO: Handle exceptions and exit with appropriate codes
client.connect(args.host, 22, args.username, args.password, timeout=30, look_for_keys=False, allow_agent=False, auth_timeout=30)

shell = client.invoke_shell()
sleep(1)
shell.recv(1024)
# Activates the menu
shell.send('\n')  # ENTER
sleep(1)
shell.recv(1024)
# Enters shell
shell.send('\x13')  # CTRL+S
sleep(1)
shell.recv(10240)
# Capture configuration
shell.send('type config.csv\n')
sleep(3)
config = shell.recv(102400)
# Disconnect
shell.send('\x18')
client.close()

# Discard not-config lines
config = '\n'.join(config.decode().splitlines()[1:-2])

print(config)
