FROM python:3.10

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    libxrender-dev

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
