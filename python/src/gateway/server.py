import os,gridfs,pika,json
from flask import Flask,request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

MONGO_URI =  os.getenv("MONGO_URI","mongodb://root:root@host.minikube.internal:27017/videos?authSource=admin")
server= Flask(__name__)
server.config["MONGO_URI"] = MONGO_URI

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/login",methods=["POST"])
def login():
    token , err = access.login(request)
    if not err:
        return token
    else:
        return err

@server.route("/upload",methods=["POST"])
def upload():
    access, err = validate.token(request)
    if err:
        return err
    if access.get("email"):
        if not len(request.files) == 1:
            return {"error":"expecting 1 file only."},400
        
        for _ , file in request.files.items():
            err = util.upload(file,fs,channel,access)

            if err:
                return err

        return {"message":"file uploaded successfuly"},201

    else:
        return {"error": "not a valid user"},401


@server.route("/download",methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0",port=8080)