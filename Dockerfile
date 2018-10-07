FROM python:3
COPY requirements.txt /src/
RUN pip install -r /src/requirements.txt

COPY . /src
CMD python /src/regexbot.py
