#!/usr/bin/env python

import sys
import requests

def cookies():
    try:
        with open('cookies.txt') as f:
            jbsession_val = f.read().rstrip()
        return {'jbsession': jbsession_val}
    except IOError:
        print 'File cookies.txt not found.'

def get_data(year):
    url = 'https://jawbone.com/user/settings/download_up_data?year=' + year
    response = requests.get(url, cookies=cookies())

    csv_file = year + '.csv'
    with open(csv_file, 'w') as f:
        f.write(response.content)

def print_help():
    print 'Usage: jawbone.py year' + '\n'
    print 'Retrieves data for the given year from the jawbone website.'

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print_help()
        sys.exit()

    year = sys.argv[1]
    get_data(year)
