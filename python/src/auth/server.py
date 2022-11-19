import jwt, datetime, os
from flask import Flask, request
import psycopg2
from cryptography.fernet import Fernet

HOST=os.getenv('HOST',"192.168.1.42")
DATABASE=os.getenv('DATABASE',"auth")
USER=os.getenv('POSTGRES_USER','auth_user')
PASSWORD=os.getenv('POSTGRES_PASSWORD','root')
JWT_SECRET = os.getenv("JWT_SECRET","some-secret")

key = Fernet.generate_key()
fernet = Fernet(key)

def get_db_connection():
    conn = psycopg2.connect(host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD)

    return conn


server = Flask(__name__)

@server.route("/api/v1/login",methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return {"error":"Authentication creds not provided"},401
    
    cur = get_db_connection().cursor()
    user = cur.execute(f"SELECT * from users where email={auth.email} and password={fernet.encrypt(auth.password.encode())}")
    if len(user) > 0:
        return {"message":"Login successfully.","token": jwt.encode(user[0],JWT_SECRET,True) },200
    return {"error":"Authentication creds not provided"},401

@server.route("/api/v1/validate",methods=["POST"])
def validate():
    token = request.headers.get("Authorization",None)
    if not token:
        return {"error":"Token not provided"},401
    _, encoded_jwt = token.split(" ")

    try:
        decoded_jwt = jwt.decode(encoded_jwt,key=JWT_SECRET,algorithm=["hs256"])
        return decoded_jwt,200
    except:
        return {"error":"Invalid token"},401

def create_jwt(user,authz):
    return jwt.encode(
        {
            "email": user.get("email"),
            "exp" : get_jwt_expiry(),
            "created_at" : datetime.datetime.now(tx=datetime.timezone.now())
        },
        key=JWT_SECRET,
        algorithm=["hs256"]
    )


def get_jwt_expiry():
    return datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)

if __name__ == "__main__":
    server.run(host="0.0.0.0",port=5000)