FROM python:3.11.3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
WORKDIR /usr/src/app
COPY . /usr/src/app

CMD ["python", "Files/bot.py"]