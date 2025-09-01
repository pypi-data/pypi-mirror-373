import requests

def delete_s3_doc(token, doc_id):
    url = "https://inthepicture.org/admin/delete_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }
    data = {
        "doc_id": doc_id,
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
