FROM python:3.11.3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app
COPY . /usr/src/app

CMD ["python", "Files/bot.py"]