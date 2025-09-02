import requests

def ask_ai_question(token, question, tapestry_id, session_id=None, group_ids=None, document_name=None,ai_type=None):
    url = "https://inthepicture.org/admin/ask_ai_question"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    
    data = {
        "question": question,
        "tapestry_id": tapestry_id
    }

    # Optional fields
    if session_id is not None:
        data["session_id"] = session_id
    if group_ids:
        data["group_ids"] = group_ids
    if document_name:
        data["documentName"] = document_name
    if ai_type:
        data["type"] = ai_type

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