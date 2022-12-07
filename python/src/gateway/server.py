import os,gridfs,pika
from bson.objectid import ObjectId
from flask import Flask,request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

VIDEOS_MONGO_URI =  os.getenv("VIDEOS_MONGO_URI","mongodb://root:root@host.minikube.internal:27017/videos?authSource=admin")
MP3S_MONGO_URI =  os.getenv("MP3S_MONGO_URI","mongodb://root:root@host.minikube.internal:27017/mp3s?authSource=admin")
server= Flask(__name__)

videos_mongo = PyMongo(server,VIDEOS_MONGO_URI)
mp3s_mongo = PyMongo(server,MP3S_MONGO_URI)

video_fs = gridfs.GridFS(videos_mongo.db)
mp3_fs = gridfs.GridFS(mp3s_mongo.db)

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
            err = util.upload(file,video_fs,channel,access)

            if err:
                return err

        return {"message":"file uploaded successfuly"},201

    else:
        return {"error": "not a valid user"},401


@server.route("/download",methods=["GET"])
def download():
    token , err = validate.token(request)

    if err :
        return err
    
    file_id = request.args.get("file_id")
    if not file_id:
        return {"error":"file_id is required."},400
    
    try:
        bin_file = mp3_fs.get(ObjectId(file_id))
        return send_file(bin_file,download_name=f"{file_id}.mp3")
    except Exception as err:
        return {"error":f"Error in getting mp3 file from DB. {str(err)}"},500




if __name__ == "__main__":
    server.run(host="0.0.0.0",port=8080)