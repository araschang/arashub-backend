FROM python:3.9.17-slim-bookworm

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 55688

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:55688", "wsgi:app"]