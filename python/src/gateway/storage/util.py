import pika, json,os
import logging

logger = logging.Logger(__name__)

def upload(file,fs,channel,access):
    try:
        file_id = fs.put(file)
    except Exception as err:
        logger.error(f"Error in uploading video. {str(err)}")
        return {"error": str(err)}, 500

    message = {
        "video_file_id" : str(file_id),
        "mp3_file_id" : None,
        "user" : access.get("email")
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("VIDEO_QUEUE","video"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs.delete(file_id)
        return {"error":str(err)},500