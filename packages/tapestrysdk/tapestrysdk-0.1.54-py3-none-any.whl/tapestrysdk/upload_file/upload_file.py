import requests

def upload_file(token, tapestry_id, file_url, file_title, description, summary, group_ids, hidden=True):
    url =  "https://inthepicture.org/admin/uplaod_file"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
        "file_url": file_url,
        "file_title": file_title,
        "description": description,
        "summary": summary,
        "group_ids": group_ids,
        "hidden": hidden
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
