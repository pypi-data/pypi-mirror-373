import requests

def selected_document_data(token, document_ids,tapestry_id,name):

    url =  "https://inthepicture.org/admin/selected_document_data"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "document_ids": document_ids,
        "tapestry_id": tapestry_id,
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