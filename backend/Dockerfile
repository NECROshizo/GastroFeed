FROM python:3.11.3-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

COPY . .

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && pip install -r requirements.txt

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]