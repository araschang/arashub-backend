FROM python:3.11.4-slim-bookworm

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 55688

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:55688", "wsgi:app", "--log-level=debug", "--timeout", "300"]