#!/usr/bin/python3
"""
Capture MikroTik device configurations. Used by CA Spectrum NCM.
"""

import argparse
import re
from time import sleep

import paramiko

parser = argparse.ArgumentParser(description='Capture MikroTik configurations')
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

shell = client.invoke_shell(term='nocolor')
sleep(1)
shell.recv(1024)
# Activates the menu
shell.send('\r\n')  # ENTER
sleep(1)
shell.recv(1024)
shell.send('/export\r\n')
sleep(1)
config = shell.recv(102400)
shell.send('quit\r\n')
client.close()

ansi_escape = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

config = [ansi_escape.sub('', line) for line in config.decode().splitlines()[3:]]
config = '\n'.join(config)

print(config)
