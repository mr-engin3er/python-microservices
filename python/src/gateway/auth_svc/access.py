import os, requests

AUTH_SVC_ADDRESS = os.getenv("AUTH_SVC_ADDRESS","localhost:5000")

def login(request):
    auth = request.authorization
    if not auth:
        return None,({"error":"missing credentials"},401)
    
    basic_auth = (auth.username,auth.password)
    response = requests.post(
        url=f"http://{AUTH_SVC_ADDRESS}/api/v1/login",
        auth=basic_auth
        )
    if response.status_code == 200:
        return (response.json(),200),None
    else:
        return None,(response.json(),response.status_code)