#!/usr/bin/python3
"""
Capture Siemens WiMAX device configurations. Used by CA Spectrum NCM.
"""

import argparse
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


def newer(file_path, mtime):
    try:
        return os.path.getmtime(file_path) > mtime
    except FileNotFoundError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Capture Siemens WiMAX configurations')
    parser.add_argument('host', type=str, help='Device ip address')
    parser.add_argument('username', type=str, help='Username for connecting')
    parser.add_argument('password', type=str, help='Password for connecting')
    parser.add_argument('enable', type=str, help='Enable password (not used)')
    parser.add_argument('timeout', type=int, default=30, help='Timeout')
    parser.add_argument('retries', type=int, default=3, help='Retries')

    args = parser.parse_args()

    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    s = requests.Session()
    s.auth = (args.username, args.password)

    base_url = 'https://{}/'.format(args.host)

    # First request get the cookie
    s.get(base_url, verify=False)

    # Second request to authtenticate an get the session number
    r = s.get(base_url, verify=False)
    if not r.ok:
        print("Invalid credentials supplied.", file=sys.stderr)
        return(4)

    # Navigate to locate the file id
    m = re.search('URL=/(.*)(m.*?)"', r.text)
    base_url += m.group(1)
    link = m.group(2)

    r = s.get(base_url+link, verify=False)
    soup = BeautifulSoup(r.text, features='html.parser')
    link = soup.find('frame', {'name': 'menuframe'}).attrs['src']

    r = s.get(base_url+link)
    soup = BeautifulSoup(r.text, features='html.parser')
    link = soup.find('td', text='Primary Bank').find('a').attrs['href']

    r = s.get(base_url+link)
    soup = BeautifulSoup(r.text, features='html.parser')
    link = soup.find('frame', {'name': 'cmdframe'}).attrs['src']

    r = s.get(base_url+link)
    soup = BeautifulSoup(r.text, features='html.parser')

    file_id = soup.find('td', text='BS-Val-Unique.xml').find_previous_sibling().find('input').attrs['value']

    # Get the date before uploading to compare the file
    now = time.time()

    # Trigger the upload
    data = {
        'MCTable_action': '',
        'MCTable_S': file_id,
        'Submit': 'Upload File'
    }
    url = base_url+link
    r = s.post(url, data=data, verify=False)
    r = s.post(url.replace('-',''), data=data, verify=False)

    # Wait for the file to appear on the FTP Server
    file_path = '/opt/ftp/{}_BS-Val-Unique.xml'.format(args.host)
    attempts = 0
    while not newer(file_path, now) and attempts < args.timeout:
        time.sleep(1)
        attempts += 1

    if attempts >= args.timeout:
        print("Timeout waiting for the file.", file=sys.stderr)
        return(3)

    with open(file_path, encoding='latin1') as fh:
        print(fh.read())

    return(0)


if __name__ == '__main__':
    exit(main())
