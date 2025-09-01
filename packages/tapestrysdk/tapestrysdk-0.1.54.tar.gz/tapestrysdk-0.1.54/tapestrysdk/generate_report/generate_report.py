import requests

def generate_report(tapestry_id, group_id, document_ids, is_chat=False, user_prompt=""):
    url = "https://inthepicture.org/admin/report_generation"
    payload = {
        "tapestry_id": tapestry_id,
        "group_id": group_id,
        "document_ids": document_ids,
        "is_chat": is_chat,
        "user_prompt": user_prompt
    }

    response = requests.post(url, json=payload)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
