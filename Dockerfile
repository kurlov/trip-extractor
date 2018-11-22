FROM python:3.7-alpine

WORKDIR /home/app

RUN apk --no-cache add build-base

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY data data
COPY processor.py file_handler.py run.py ./

ENTRYPOINT ["./venv/bin/python", "run.py"]
