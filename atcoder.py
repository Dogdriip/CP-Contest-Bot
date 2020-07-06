import requests
from bs4 import BeautifulSoup
from datetime import *
import time

ATCODER_URL = 'https://atcoder.jp'

def get_contests():
    ret = {}  # return dict

    req = requests.get(ATCODER_URL + '/contests')
    if req.status_code != 200:
        ret['fetch'] = False
        return ret
    else:
        ret['fetch'] = True

    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    contests = soup.select('#contest-table-upcoming > div > div > table > tbody > tr')
    # contests = soup.select('#contest-table-recent > div > div > table > tbody > tr')

    ret['contests'] = []

    for x in contests:
        starts_str = x.select_one('td:nth-child(1) > a').text
        starts = time.mktime(datetime.strptime(starts_str, '%Y-%m-%d %H:%M:%S%z').timetuple())
        name = x.select_one('td:nth-child(2) > a').text
        url = x.select_one('td:nth-child(2) > a').get('href')
        duration_str = x.select_one('td:nth-child(3)').text
        h, m = map(int, duration_str.split(':'))
        duration = h * 60 * 60 + m * 60
        ends = starts + duration
        
        ret['contests'].append({
            'name': name,
            'starts': starts,
            'ends': ends,
            'duration': duration,
            'url': ATCODER_URL + url
        })

    return ret