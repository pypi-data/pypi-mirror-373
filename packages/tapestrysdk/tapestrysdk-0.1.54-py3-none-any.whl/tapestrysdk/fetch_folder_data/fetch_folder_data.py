import requests

def fetch_folder_data(token, folder_details):
    folder_name = folder_details.get("name")
    tapestry_id = folder_details.get("tapestry_id")

    url =  "https://inthepicture.org/admin/library"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "page": 1,
        "active": "grid",
        "group_id": [],
        "tapestry_id": tapestry_id,
        "parent": folder_name,
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
token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Nywicm9sZSI6bnVsbCwiYWRtaW5faWQiOjAsIm90cCI6MCwiaXNfdmVyaWZpZWQiOjAsIm9yZ19pZCI6MCwiaXNfYmxvY2siOjAsInBhc3N3b3JkIjoiIiwibmFtZSI6Ik1laHVsIEthdXNoYWwiLCJmaXJzdF9uYW1lIjoiTWVodWwiLCJzdHJpcGVfY3VzdG9tZXJfaWQiOiJjdXNfU255Z3lobzJUd1dZUlEiLCJpc193ZWxjb21lX21lc3NhZ2Vfc2hvd24iOjEsImlzX3B1YmxpYyI6MCwiYWJvdXQiOm51bGwsInZvaWNlIjoiSm9hbm5hIiwiaW1hZ2UiOiIiLCJsYXN0X25hbWUiOiJLYXVzaGFsIiwibmlja19uYW1lIjoiIiwiZW1haWwiOiJtZWh1bC5kdWNrdGFsZUBnbWFpbC5jb20iLCJmb3Jnb3RQYXNzd29yZEhhc2giOiIiLCJjaGF0X2lkIjoiIiwiZ29vZ2xlX2lkIjoiMTEwMzYxMDI2MjYwODIxNjQxMzcxIiwic2VjcmV0X2tleSI6InFuakg1emNqd2ZQVDRYMVZialpFbExmVCIsInBob25lIjoiIiwidGltZVpvbmUiOiJVVEMiLCJtZmFfdHlwZSI6MywiZ29vZ2xlX3NlY3JldCI6IiIsImlzX3FyX3NjYW5uZWQiOjAsImNyZWF0ZWRBdCI6IjIwMjUtMDgtMDRUMTE6Mzk6MTIuMDAwWiIsInVwZGF0ZWRBdCI6IjIwMjUtMDgtMjVUMTI6MTc6MTYuMDAwWiIsImlzX21vZGVyYXRvciI6MCwidW5pcXVlTmFtZSI6bnVsbCwiaWF0IjoxNzU2MTI0MjM2LCJleHAiOjE3NTYyMTA2MzZ9.zu4mRF_8kNuQp4Mc637PsTpLMaTWhIC6ZREnQemgVzA"
folder_details={"tapestry_id":13,"name":"fun_activity"}
res=fetch_folder_data(token,folder_details)
print(res)