#!/usr/bin/python3
"""
Capture CISCO IOS device configurations. Used by CA Spectrum NCM
"""

import re
import sys

from netmiko import ConnectHandler, NetMikoAuthenticationException

HOSTNAME = sys.argv[1]
USER = sys.argv[2]
PASS = sys.argv[3]
ENABLE = sys.argv[4]
TIMEOUT = int(sys.argv[5])
CONFIG_TYPE = sys.argv[6] if len(sys.argv) > 6 else 'running'

GLOBAL_DELAY_FACTOR = 2
SHOW_DELAY_FACTOR = 5


def main():
    cisco_device = {
        'device_type': 'cisco_ios_telnet',
        'ip': HOSTNAME,
        'username': USER,
        'password': PASS,
        'secret': ENABLE,
        'timeout': TIMEOUT,
        'global_delay_factor': GLOBAL_DELAY_FACTOR
    }

    try:
        net_connect = ConnectHandler(**cisco_device)
    except NetMikoAuthenticationException:
        cisco_device['password'] = ENABLE
        try:
            net_connect = ConnectHandler(**cisco_device)
        except NetMikoAuthenticationException:
            print('Authentication Error', file=sys.stderr)
            exit(251)
    except Exception:
        print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
        exit(1)

    try:
        net_connect.enable()
    except Exception:
        pass

    output = ''

    if CONFIG_TYPE == 'startup':
        output = net_connect.send_command('show startup-config', delay_factor=SHOW_DELAY_FACTOR)
    elif CONFIG_TYPE == 'running':
        output = net_connect.send_command('show running-config', delay_factor=SHOW_DELAY_FACTOR)
    else:
        net_connect.disconnect()
        print('Invalid configuration type.\nPlease specify either running or startup', file=sys.stderr)
        exit(5)

    output.lstrip()
    conf = ''

    for line in output.split('\n'):
        if not re.match('^(Using|Building configuration|Current configuration)', line):
            conf += line + '\n'

    print(conf.lstrip())

    net_connect.disconnect()


if __name__ == '__main__':
    main()
