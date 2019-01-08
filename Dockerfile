FROM alpine:3.8
RUN apk add -U python3
COPY requirements.txt /src/
RUN pip3 install -r /src/requirements.txt
COPY . /src
CMD python3 /src/regexbot.py
