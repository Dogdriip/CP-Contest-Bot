import json
from datetime import *
import time
import requests
import os
# import codeforces, atcoder

KST = timezone(timedelta(hours=9))
WEBHOOK_INFO_FILE = "webhook_info.json"

def lambda_func(event, context):
    webhook_info = json.load(open(WEBHOOK_INFO_FILE, "r"))
    webhook_url = webhook_info["INCOMING_WEBHOOK_URL"]

    attachments = []  # for payloads. final result goes here

    now = datetime.now(KST)
    now_s = now.strftime("%Y-%m-%d %H:%M:%S")

    





    """
    Send post to slack webhook, return response from lambda.
    """

    """
    payloads = {
        'text': f'{now_s} 기준 콘테스트 목록',
        'attachments': attachments
    }

    req = requests.post(
        WEBHOOK_URL,
        data=json.dumps(payloads),
        headers={'Content-Type': 'application/json'}
    )
    """

    # temp!

    response = {}
    if True:
    # if req.status_code != 200:
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Succeed",
                "input": event
            })
        }
    else:
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed",
                "input": event
            })
        }


    return response