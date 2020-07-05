import json
from datetime import *
import time
import requests
import os
import codeforces, atcoder

KST = timezone(timedelta(hours=9))
WEBHOOK_INFO_FILE = "webhook_info.json"

def lambda_func(event, context):
    """
    Configure variables.
    """
    # Final response detail from this function.
    response_detail = {}
    # Webhook info.
    webhook_info = json.load(open(WEBHOOK_INFO_FILE, "r"))
    webhook_url = webhook_info["INCOMING_WEBHOOK_URL"]
    # For slack payloads. final result (contest lists) goes here.
    attachments = []
    # Now datetime.
    now = datetime.now(KST)
    now_s = now.strftime("%Y-%m-%d %H:%M:%S")

    """
    Get Codeforces contests list.
    """
    cf_list = codeforces.get_contests()
    if not cf_list["fetch"]:
        # if Codeforces fetch fails
        attachments.append({
            "color": "#FF0000",
            "fields": [{
                "value": "Error fetching Codeforces!"
            }]
        })
        response_detail["codeforces_result"] = "failed"
        response_detail["codeforces_body"] = ""
    else:
        # print(cf_list)
        for x in cf_list["contests"]:
            # Contest name.
            name = x["name"]
            # Contest starts.
            starts = datetime.fromtimestamp(x["startTimeSeconds"], KST)
            starts_s = starts.strftime("%Y-%m-%d %H:%M")
            # Contest ends.
            ends = datetime.fromtimestamp(x["startTimeSeconds"] + x["durationSeconds"], KST)
            ends_s = ends.strftime("%Y-%m-%d %H:%M")
            # Contest URL.
            url = f'https://codeforces.com/contests/{x["id"]}'

            # For attach text (Remaining time)
            starts_delta = starts - now
            attach_text = ""
            if starts_delta.days != 0:
                attach_text += f"{starts_delta.days}일 "
            attach_text += f"{starts_delta.seconds // 3600}시간 후에 시작해요!"

            attachments.append({
                "mrkdwn_in": ["text"],
                "color": "#FFBE5C",
                "title": name,
                "text": attach_text,
                "fields": [
                    {
                        "title": "시작 일시",
                        "value": starts_s,
                        "short": True
                    },
                    {
                        "title": "종료 일시",
                        "value": ends_s,
                        "short": True
                    },
                    {
                        "title": "대회 URL",
                        "value": url,
                        "short": True
                    }
                ]
            })
        response_detail["codeforces_result"] = "succeed"
        response_detail["codeforces_body"] = cf_list
    
    """
    Get Atcoder contests list.
    """
    at_list = atcoder.get_contests()
    if not at_list['fetch']:
        # if Atcoder fetch fails
        attachments.append({
            "color": "#FF0000",
            "fields": [{
                "value": "Error fetching Atcoder!"
            }]
        })
        response_detail["atcoder_result"] = "failed"
        response_detail["atcoder_body"] = ""
    else:
        # print(at_list)
        for x in at_list["contests"]:
            # Contest name.
            name = x["name"]
            # Contest starts.
            starts = datetime.fromtimestamp(x["starts"], KST)
            starts_s = starts.strftime("%Y-%m-%d %H:%M")
            # Contest ends.
            ends = datetime.fromtimestamp(x["ends"], KST)
            ends_s = ends.strftime("%Y-%m-%d %H:%M")
            # Contest URL.
            url = x["url"]

            # For attach text (Remaining time)
            starts_delta = starts - now
            attach_text = ""
            if starts_delta.days != 0:
                attach_text += f"{starts_delta.days}일 "
            attach_text += f"{starts_delta.seconds // 3600}시간 후에 시작해요!"

            attachments.append({
                "mrkdwn_in": ["text"],
                "color": "#9D3757",
                "title": name,
                "text": attach_text,
                "fields": [
                    {
                        "title": "시작 일시",
                        "value": starts_s,
                        "short": True
                    },
                    {
                        "title": "종료 일시",
                        "value": ends_s,
                        "short": True
                    },
                    {
                        "title": "대회 URL",
                        "value": url,
                        "short": True
                    }
                ]
            })
        response_detail["atcoder_result"] = "succeed"
        response_detail["atcoder_body"] = at_list

    """
    Send post to slack webhook, return response from lambda.
    """
    payloads = {
        "text": f"{now_s} 기준 콘테스트 목록",
        "attachments": attachments
    }

    req = requests.post(
        webhook_url,
        data=json.dumps(payloads),
        headers={"Content-Type": "application/json"}
    )
    
    response = {}
    if req.status_code == 200:
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Slack Webhook succeed!",
                "detail": response_detail
            })
        }
    else:
        response = {
            "statusCode": req.status_code,
            "body": json.dumps({
                "message": "Slack Webhook failed!",
                "detail": response_detail
            })
        }

    return response
