import os
import requests
import subprocess
from fastapi import FastAPI, BackgroundTasks
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PEXELS_KEY = os.getenv("PEXELS_API_KEY")


def get_script():
    print("STEP 1: Generating script...")
    prompt = "Produce a 60 second YouTube script about an interesting fact."
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = res.choices[0].message.content
    print("Script OK")
    return text


def tts(text):
    print("STEP 2: Creating TTS...")
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    data = {"model": "gpt-4o-mini-tts", "voice": "alloy", "input": text}
    r = requests.post(url, headers=headers, json=data)
    print("TTS status:", r.status_code)
    with open("/app/voice.mp3", "wb") as f:
        f.write(r.content)
    print("voice.mp3 created")


def get_image():
    print("STEP 3: Downloading image...")
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(
        "https://api.pexels.com/v1/search?query=nature&per_page=1",
        headers=headers,
    )
    print("Pexels status:", r.status_code)
    img = r.json()["photos"][0]["src"]["original"]
    img_data = requests.get(img).content
    with open("/app/img.jpg", "wb") as f:
        f.write(img_data)
    print("img.jpg created")


def make_video():
    print("FILES:", os.listdir())

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", "/app/img.jpg",
        "-i", "/app/voice.mp3",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "/app/video.mp4",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("FFMPEG STDOUT:", result.stdout)
    print("FFMPEG STDERR:", result.stderr)


def process_video():
    script = get_script()
    tts(script)
    get_image()
    make_video()


@app.get("/make")
def make(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video)
    return {"status": "started"}


@app.get("/video")
def video():
    from fastapi.responses import FileResponse
    return FileResponse("video.mp4")
