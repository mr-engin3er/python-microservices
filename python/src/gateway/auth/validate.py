import os , requests

AUTH_SVC_ADDRESS = os.getenv("AUTH_SVC_ADDRESS","localhost:5000")


def token(request):
    token = request.headers.get("Authorization")
    if not token:
        return None,({"error":"Auth token required."},401)
    
    response = requests.post(
        url = f"http://{AUTH_SVC_ADDRESS}/api/v1/validate",
        headers={"Authorization":token}
    )

    if response.status_code == 200:
        return response.json(),None
    else:
        return None,(response.json(),response.status_code)
