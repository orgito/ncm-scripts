#!/usr/bin/python3
"""
Capture DELL FTOS device configurations. Used by CA Spectrum NCM
"""

import re
import sys

from unha import Unha

HOSTNAME = sys.argv[1]
USER = sys.argv[2]
PASS = sys.argv[3]
ENABLE = sys.argv[4]
TIMEOUT = int(sys.argv[5])
CONFIG_TYPE = sys.argv[6] if len(sys.argv) > 6 else 'running'


def main():
    try:
        net_connect = Unha(HOSTNAME, USER, PASS)
        net_connect.enable()
    except Exception:
        print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
        exit(1)

    output = ''

    if CONFIG_TYPE == 'startup':
        output = net_connect.send_command('show startup-config')
    elif CONFIG_TYPE == 'running':
        output = net_connect.send_command('show running-config')
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
