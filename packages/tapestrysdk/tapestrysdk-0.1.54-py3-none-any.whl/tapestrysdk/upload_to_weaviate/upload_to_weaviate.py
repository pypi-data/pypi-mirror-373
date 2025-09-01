import requests

def upload_to_weaviate(tapestry_id, chunks):
    url =  "https://inthepicture.org/admin/upload_to_weaviate"

    payload = {
        "tapestry_id": tapestry_id,
        "chunks": chunks,
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