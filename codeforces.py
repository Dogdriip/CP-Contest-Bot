import requests

CF_API = 'https://codeforces.com/api/contest.list'

def get_contests():
    ret = {}  # return dict

    req = requests.get(CF_API).json()  # convert to python dict
    if req['status'] != 'OK':
        ret['fetch'] = False
    else:
        ret['fetch'] = True

    res = req['result']
    before_contest_list = [x for x in res if x['phase'] == 'BEFORE']

    ret['contests'] = before_contest_list

    return ret