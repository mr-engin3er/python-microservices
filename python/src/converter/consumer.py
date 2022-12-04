import os, pika,sys, gridfs
from pymongo import MongoClient
from convert import to_mp3

MONGO_HOST = os.getenv("MONGO_HOST","mongodb://root:root@host.minikube.internal")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST","rabbitmq")
VIDEO_QUEUE = os.getenv("VIDEO_QUEUE","video")
def main():
    # mongo client 
    mongo_client = MongoClient(MONGO_HOST,27017)
    db_videos = mongo_client.videos
    db_mp3s = mongo_client.mp3s

    # fs clients
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq client
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    def message_callback(channel,method,properties,body):
        err = to_mp3.start(body,fs_videos,fs_mp3s,channel)
        if err:
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=VIDEO_QUEUE,on_message_callback=message_callback)
    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)