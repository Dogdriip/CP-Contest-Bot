import json
from datetime import *
import time
import requests
import os
import codeforces, atcoder

KST = timezone(timedelta(hours=9))
WEBHOOK_INFO_FILE = "webhook_info.json"
COLOR = {
    "codeforces": "#FFBE5C",
    "atcoder": "#9D3757",
    "error": "#FF0000"
}

def lambda_func(event, context):
    """
    Configure variables.
    """
    # Final response detail from this function.
    response_detail = {}
    # Webhook info.
    webhook_info = json.load(open(WEBHOOK_INFO_FILE, "r"))
    webhook_url = webhook_info["INCOMING_WEBHOOK_URL"]
    # Contests list. It'll be sorted and converted into attachments list.
    contests = []
    # Now datetime.
    now = datetime.now(KST)
    now_s = now.strftime("%Y-%m-%d %H:%M:%S")

    """
    Get Codeforces contests list.
    """
    cf_list = codeforces.get_contests()
    if not cf_list["fetch"]:
        # if Codeforces fetch fails
        contests.append({
            "type": "error",
            "detail": "Error fetching Codeforces!"
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
            # Contest ends.
            ends = datetime.fromtimestamp(x["startTimeSeconds"] + x["durationSeconds"], KST)
            # Contest URL.
            url = f'https://codeforces.com/contests/{x["id"]}'
            # Remaining time until contest starts.
            remaining_time = starts - now

            contests.append({
                "type": "codeforces",
                "name": name,
                "starts": starts,
                "ends": ends,
                "url": url,
                "remaining_time": remaining_time
            })
        
        response_detail["codeforces_result"] = "succeed"
        response_detail["codeforces_body"] = cf_list
    
    """
    Get Atcoder contests list.
    """
    at_list = atcoder.get_contests()
    if not at_list['fetch']:
        # if Atcoder fetch fails
        contests.append({
            "type": "error",
            "detail": "Error fetching Atcoder!"
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
            starts -= timedelta(hours=9)  # 이건 좀 아니지
            # Contest ends.
            ends = datetime.fromtimestamp(x["ends"], KST)
            ends -= timedelta(hours=9)  # ㅁㄴㅇㄹ
            # Contest URL.
            url = x["url"]
            # Remaining time until contest starts.
            remaining_time = starts - now

            contests.append({
                "type": "atcoder",
                "name": name,
                "starts": starts,
                "ends": ends,
                "url": url,
                "remaining_time": remaining_time
            })
        
        response_detail["atcoder_result"] = "succeed"
        response_detail["atcoder_body"] = at_list

    """
    Build `attachments` list from `contests` list.
    This'll be used in slack payloads.
    """
    # Sort contests by remaining time.
    contests.sort(key=lambda contest: contest["remaining_time"])

    # For slack payloads. final result (contest lists) goes here.
    attachments = []
    for contest in contests:
        # Format starts, ends time to string.
        starts_str = contest["starts"].strftime("%Y-%m-%d %H:%M")
        ends_str = contest["ends"].strftime("%Y-%m-%d %H:%M")
        # Remaining time to body text.
        remaining_time = contest["remaining_time"]
        body_text = ""
        if remaining_time.days != 0:
            body_text += f"{remaining_time.days}일 "
        body_text += f"{remaining_time.seconds // 3600}시간 후에 시작해요!"
        
        # Configure attachments ('ll be used in slack payloads.)
        attachments.append({
            "mrkdwn_in": ["text"],
            "color": COLOR[contest["type"]],
            "title": contest["name"],
            "text": body_text,
            "fields": [
                {
                    "title": "시작 일시",
                    "value": starts_str,
                    "short": True
                },
                # {
                #     "title": "종료 일시",
                #     "value": ends_str,
                #     "short": True
                # },
                {
                    "title": "대회 URL",
                    "value": contest["url"],
                    "short": True
                }
            ]
        })

    """
    Send post to slack webhook, return response from lambda.
    """
    payloads = {
        "text": f"{now_s} 기준 콘테스트 목록입니다.",
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
