import requests
from io import BytesIO
import os

def update_s3_doc(token, doc_id, blob, content_type=None):
    url = "https://inthepicture.org/admin/update_s3_doc"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }

    # Determine if blob is a file path or raw content
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like = open(blob, "rb")
    else:
        if isinstance(blob, str):
            blob = blob.encode('utf-8')
        file_like = BytesIO(blob)

    files = {
        "blob": ("file", file_like, content_type),
    }
    data = {
        "doc_id": doc_id,
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    # Close file if opened from disk
    if isinstance(blob, str) and os.path.isfile(blob):
        file_like.close()

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        return {
            "success": False,
            "code": response.status_code,
            "message": resp_json.get("message", response.text),
            "body": {}
        }
