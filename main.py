import os
import requests
from fastapi import FastAPI
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
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

def get_image(query):
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(
        f"https://api.pexels.com/v1/search?query={query}&per_page=1",
        headers=headers,
    )
    img = r.json()["photos"][0]["src"]["original"]
    img_data = requests.get(img).content
    with open("img.jpg", "wb") as f:
        f.write(img_data)

def make_video():
    audio = AudioFileClip("voice.mp3")
    img = ImageClip("img.jpg").set_duration(audio.duration)
    video = img.set_audio(audio)
    video.write_videofile("video.mp4", fps=24)

@app.get("/make")
def make():
    script = get_script()
    tts(script)
    get_image("nature")
    make_video()
    return {"status": "video_created"}
