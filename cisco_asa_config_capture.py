#!/usr/bin/python3
# pylint: disable=C0111
"""
Capture CISCO ASA device configurations. Used by CA Spectrum NCM
"""

import re
import sys

from netmiko import (ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException)

HOSTNAME = sys.argv[1]
USER = sys.argv[2]
PASS = sys.argv[3]
ENABLE = sys.argv[4]
TIMEOUT = int(sys.argv[5])
CONFIG_TYPE = sys.argv[6] if len(sys.argv) > 6 else'running'
ENABLE_LEVEL = int(sys.argv[7]) if len(sys.argv) > 7 else 15

GLOBAL_DELAY_FACTOR = 2
SHOW_DELAY_FACTOR = 5


def enable_level(net_connect, level=1):
    if level < 15:
        prompt = net_connect.find_prompt().replace('/', '.')
        net_connect.send_command('enable {}'.format(level), expect_string='ssword:')
        net_connect.send_command(net_connect.secret, expect_string=prompt)
        return
    try:
        net_connect.enable()
    except Exception:
        return


def get_conf(net_connect, command):
    prompt = net_connect.find_prompt().replace('/', '.') # Without this hack send_command hangs forever
    output = net_connect.send_command(command, delay_factor=SHOW_DELAY_FACTOR, expect_string=prompt).lstrip()

    conf = ''
    for line in output.split('\n'):
        if not re.match('^(Using|Building configuration|Current configuration)', line):
            conf += line + '\n'

    return conf.lstrip()


def main():
    cisco_device = {
        'device_type': 'cisco_asa',
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

    enable_level(net_connect, ENABLE_LEVEL)

    net_connect.send_command('terminal pager 0')

    if CONFIG_TYPE == 'startup':
        command = 'show startup-config'
    elif CONFIG_TYPE == 'running':
        command = 'show running-config'
    else:
        net_connect.disconnect()
        print('Invalid configuration type.\nPlease specify either running or startup', file=sys.stderr)
        exit(5)

    # check if the firewall is in multiple or single context mode
    asamode = net_connect.send_command('show mode', delay_factor=SHOW_DELAY_FACTOR)

    output = ''
    if 'multiple' in asamode:
        output = 'ATTENTION: MULTIPLE CONTEXT MODE'.center(80, '!') + '\n'

        # change to system context and get the configuration
        net_connect.send_command('changeto system')
        systemconf = get_conf(net_connect, command)
        output += '\n' + 'System Config'.center(80, '!') + '\n' + systemconf + '\n'

        # get the list of contexts
        contexts = re.findall(r'^context (\w+)$', systemconf, re.MULTILINE)

        # get the configuration of each context
        for context in contexts:
            net_connect.send_command('changeto context {}'.format(context))
            output += '\n' + 'Context {} Config'.format(context).center(80, '!') + '\n'
            output += get_conf(net_connect, command)
    else: # Assume single mode
        output = get_conf(net_connect, command)

    net_connect.disconnect()

    print(output)


if __name__ == '__main__':
    main()
