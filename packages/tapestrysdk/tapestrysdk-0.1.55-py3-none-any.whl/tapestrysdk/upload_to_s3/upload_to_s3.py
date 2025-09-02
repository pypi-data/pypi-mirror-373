import requests
from io import BytesIO
import os
import mimetypes
import re

MIME_REGEX = re.compile(r'^[a-zA-Z0-9!#$&^_.+-]+/[a-zA-Z0-9!#$&^_.+-]+$')

def validate_content_type(content_type=None, file_name=None):
    # If user passed content_type, validate it
    if content_type:
        if not MIME_REGEX.match(content_type):
            raise ValueError(f"Invalid content_type format: {content_type}")
        
        # Known MIME types list from Python
        known_mime_types = set(mimetypes.types_map.values())
        if content_type in known_mime_types:
            return content_type
        else:
            # Allow custom but valid format → fallback
            return content_type  # or raise error if you want strict mode
    
    # If not provided, try guessing from file name
    if file_name:
        guessed, _ = mimetypes.guess_type(file_name)
        return guessed or "application/octet-stream"
    
    # Fallback
    return "application/octet-stream"

def upload_to_s3(token, tapestry_id, blob, doc_name, key, content_type=None ):
    url = "https://inthepicture.org/admin/upload_to_s3"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
    }

    # ✅ Check if blob is a Jupyter FileUpload-like dict with MIME type
    if isinstance(blob, dict) and "content" in blob:
        file_data = blob["content"]
        if isinstance(file_data, str):
            file_data = file_data.encode('utf-8')
        # Use blob's own type if available and no explicit content_type
        if content_type is None and "type" in blob and blob["type"]:
            content_type = blob["type"]
    else:
        # Handle normal file path or raw content
        if isinstance(blob, str) and os.path.isfile(blob):
            file_data = open(blob, "rb")
        else:
            if isinstance(blob, str):
                blob = blob.encode("utf-8")
            file_data = BytesIO(blob)

    # ✅ Validate or infer content type (from explicit param or filename)
    content_type = validate_content_type(content_type, file_name=doc_name)

    files = {
        "blob": (doc_name, file_data, content_type),
    }
    data = {
        "tapestry_id": tapestry_id,
        "doc_name": doc_name,
        "key": key,
    }
    response = requests.post(url, headers=headers, files=files, data=data)

    # Close file if it was opened from disk
    if isinstance(blob, str) and os.path.isfile(blob):
        file_data.close()

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
