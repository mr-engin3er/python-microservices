import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor

def start(body,fs_videos,fs_mp3s,channel):
    message = json.loads(body)

    # empty temp file
    temp_video = tempfile.NamedTemporaryFile()
    # get video file
    video = fs_videos.get(ObjectId(message["video_file_id"]))
    temp_video.write(video.read())

    # convert to audio 
    audio = moviepy.editor.VideoFileClip(temp_video.name).audio
    temp_video.close()

    mp3_file_path = tempfile.gettempdir() + f'/{message["video_file_id"]}.mp3'
    audio.write_audiofile(mp3_file_path)

    # write to database
    f = open(mp3_file_path,"rb")
    data = f.read()
    mp3_file_id = fs_mp3s.put(data)

    #close open file and delete temp mp3 file
    f.close()
    os.remove(mp3_file_path)

    message["mp3_file_id"] = str(mp3_file_id)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.getenv("MP3_QUEUE","mp3"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs_mp3s.delete(mp3_file_id)
        return f"Failed to publish. Err is {err}"
