import requests

def fetch_group_list(tapestry_id):
    url = "https://inthepicture.org/admin/fetch_group_list"
    params = {
        "tapestry_id": tapestry_id
    }

    response = requests.get(url, params=params)
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
