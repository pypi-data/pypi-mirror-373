import requests

def fetch_sticky_notes(token, tapestry_id, tapestry_user_id, name):
    url =  "https://inthepicture.org/admin/fetch_sticky_notes"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "tapestry_user_id": tapestry_user_id,
        "name": name
    }
    response = requests.post(url, headers=headers, json=data)
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