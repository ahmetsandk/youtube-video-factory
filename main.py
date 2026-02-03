import os
import requests
import subprocess
from fastapi import FastAPI, BackgroundTasks
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PEXELS_KEY = os.getenv("PEXELS_API_KEY")


def get_script():
    prompt = "Produce a 60 second YouTube script about an interesting fact."
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


def tts(text):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    data = {"model": "gpt-4o-mini-tts", "voice": "alloy", "input": text}
    r = requests.post(url, headers=headers, json=data)
    with open("voice.mp3", "wb") as f:
        f.write(r.content)


def get_image():
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(
        "https://api.pexels.com/v1/search?query=nature&per_page=1",
        headers=headers,
    )
    img = r.json()["photos"][0]["src"]["original"]
    img_data = requests.get(img).content
    with open("img.jpg", "wb") as f:
        f.write(img_data)


def make_video():
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", "img.jpg",
        "-i", "voice.mp3",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "video.mp4",
    ]
    subprocess.run(cmd)


def process_video():
    script = get_script()
    tts(script)
    get_image()
    make_video()


@app.get("/make")
def make(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video)
    return {"status": "started"}
