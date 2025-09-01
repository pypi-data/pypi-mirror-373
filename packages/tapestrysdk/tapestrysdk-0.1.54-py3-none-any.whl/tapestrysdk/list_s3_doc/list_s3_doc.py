import requests

def list_s3_doc(token, tapestry_id=0, **kwargs):
    # Allow alternative spelling `tapstry_id`
    if "tapstry_id" in kwargs and tapestry_id == 0:
        tapestry_id = kwargs["tapstry_id"]

    url = "https://inthepicture.org/admin/list_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "tapestry_id": tapestry_id,
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
