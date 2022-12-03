import jwt, datetime, os
from flask import Flask, request
import psycopg2
import psycopg2.extras
from werkzeug.security import check_password_hash


HOST=os.getenv('HOST',"192.168.1.4")
DATABASE=os.getenv('DATABASE',"auth")
USER=os.getenv('POSTGRES_USER','root')
PASSWORD=os.getenv('POSTGRES_PASSWORD','root')
JWT_SECRET = os.getenv("JWT_SECRET","some-secret")


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
    
    cur = get_db_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * from users where email='{auth.username}'")
    user = dict(cur.fetchone())
    if user and check_password_hash(user.get("password"),auth.password):
        return {"message":"Login successfully.","token": create_jwt(user,True) },200
    return {"error":"Authentication creds not provided"},401

@server.route("/api/v1/validate",methods=["POST"])
def validate():
    token = request.headers.get("Authorization",None)
    if not token:
        return {"error":"Token not provided"},401
    _, encoded_jwt = token.split(" ")

    try:
        decoded_jwt = jwt.decode(encoded_jwt,key=JWT_SECRET,algorithms=["HS256"])
        return decoded_jwt,200
    except:
        return {"error":"Invalid token"},401

def create_jwt(user,authz):
    return jwt.encode(
        {
            "email": user.get("email"),
            "exp" : get_jwt_expiry(),
            "created_at" : str(datetime.datetime.utcnow())
        },
        key=JWT_SECRET,
        algorithm="HS256"
    )


def get_jwt_expiry():
    return datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)

if __name__ == "__main__":
    server.run(host="0.0.0.0",port=5000)