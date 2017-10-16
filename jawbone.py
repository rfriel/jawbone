import requests

def cookies():
    with open('cookies.txt') as f:
        jbsession_val = f.read().rstrip()
    return {'jbsession': jbsession_val}

def get_data(year):
    url = 'https://jawbone.com/user/settings/download_up_data?year=' + str(year)
    response = requests.get(url, cookies=cookies())

    with open(str(year) + '.csv','w') as f:
        f.write(response.content)
