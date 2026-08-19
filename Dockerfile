FROM python:3.14
WORKDIR /src
EXPOSE 8000

RUN pip install poetry

COPY pyproject.toml poetry.lock /src
RUN poetry install --no-root

COPY . /src
CMD ["poetry", "run", "python", "/src/regexbot.py"]
