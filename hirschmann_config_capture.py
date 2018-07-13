#!/usr/bin/python3
"""
Capture Hirschmann device configurations. Used by CA Spectrum NCM
"""

import argparse
import re
import sys

from netmiko import (ConnectHandler, NetMikoAuthenticationException,
                     NetMikoTimeoutException)

GLOBAL_DELAY_FACTOR = 2
SHOW_DELAY_FACTOR = 5

parser = argparse.ArgumentParser(description='Capture RuggedCom configurations')
parser.add_argument('host', type=str, help='Device ip address')
parser.add_argument('username', type=str, help='Username for connecting')
parser.add_argument('password', type=str, help='Passwrod for connecting')
parser.add_argument('enable', type=str, help='Enable passwrod')
parser.add_argument('timeout', type=int, help='Connection and commands timeout')
# CA Spectrum may send extra, unnecessary arguments
parser.add_argument('dummy', type=str, nargs="*", help='Extra discarded arguments')
args = parser.parse_args()

device = {
    'device_type': 'cisco_ios',
    'ip':   args.host,
    'username': args.username,
    'password': args.password,
    'secret': args.enable,
    'timeout': args.timeout,
    'global_delay_factor': GLOBAL_DELAY_FACTOR
}

try:
    hirschmann = ConnectHandler(**device)
except NetMikoTimeoutException:
    device['device_type'] = 'cisco_ios_telnet'
    try:
        hirschmann = ConnectHandler(**device)
    except NetMikoTimeoutException:
        print('Connection Timeout', file=sys.stderr)
        exit(3)
    except NetMikoAuthenticationException:
        print('Authentication Error', file=sys.stderr)
        exit(251)
    except Exception:
        print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
        exit(1)
except NetMikoAuthenticationException:
    print('Authentication Error', file=sys.stderr)
    exit(252)
except Exception:
    print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
    exit(1)

try:
    hirschmann.enable()
except Exception:
    pass

output = hirschmann.send_command('show running-config all', delay_factor=SHOW_DELAY_FACTOR)

output.lstrip()
conf = ''

for line in output.split('\n'):
    if not re.match('^(Using|Building configuration|Current configuration)', line):
        conf += line + '\n'

print(conf.lstrip())

hirschmann.disconnect()
