#!/usr/bin/python3
"""
Capture Cisco Nexus 7k device configurations. Used by CA Spectrum NCM
"""

import re
import sys

from netmiko import (ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException)

HOSTNAME = sys.argv[1]
USER = sys.argv[2]
PASS = sys.argv[3]
ENABLE = sys.argv[4]
TIMEOUT = int(sys.argv[5])
CONFIG_TYPE = sys.argv[6] if len(sys.argv) > 6 else 'running'

GLOBAL_DELAY_FACTOR = 2
SHOW_DELAY_FACTOR = 5


def main():
    """Connect to the device"""
    cisco_device = {
        'device_type': 'cisco_nxos',
        'ip':   HOSTNAME,
        'username': USER,
        'password': PASS,
        'secret': ENABLE,
        'timeout': TIMEOUT,
        'global_delay_factor': GLOBAL_DELAY_FACTOR
    }

    try:
        net_connect = ConnectHandler(**cisco_device)
    except NetMikoTimeoutException:
        print('Connection Timeout', file=sys.stderr)
        exit(3)
    except NetMikoAuthenticationException:
        print('Authentication Error', file=sys.stderr)
        exit(252)
    except Exception:
        print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
        exit(1)

    # Enter enable mode
    try:
        net_connect.enable()
    except Exception:
        print('Unable to enter enable mode', file=sys.stderr)
        exit(252)

    if CONFIG_TYPE == 'startup':
        command = 'show startup-config vdc-all'
    elif CONFIG_TYPE == 'running':
        command = 'show running-config vdc-all'
    else:
        net_connect.disconnect()
        print('Invalid configuration type.\nPlease specify either running or startup', file=sys.stderr)
        exit(5)

    output = net_connect.send_command(command)

    net_connect.disconnect()

    print(output)


if __name__ == '__main__':
    main()



