import requests

def create_topic(token, tapestry_id, name, adminId, description="", member_ids=[]):
    url = "https://inthepicture.org/admin/create_organisation_group"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }
    data = {
        "tapestry_id": tapestry_id,
        "name": name,
        "adminId": adminId,
        "description": description,
        "member_ids": member_ids
    }

    response = requests.post(url, headers=headers, data=data)

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

