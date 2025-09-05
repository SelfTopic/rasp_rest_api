FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false &&\
    poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["poetry", "run", "python", "-m", "src"]
