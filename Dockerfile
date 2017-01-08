FROM python
COPY . /src
RUN pip install -r /src/requirements.txt
CMD python /src/regexbot.py
