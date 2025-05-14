FROM public.ecr.aws/docker/library/python:3.12-slim AS build

RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==2.1.2

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

FROM public.ecr.aws/docker/library/python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONOPTIMIZE 2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl

WORKDIR /app

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY binny_buddy/ /app/binny_buddy
COPY manage.py .env /app/

ARG CI=1
RUN python -OO manage.py check --deploy || exit 1

EXPOSE 8000

CMD [ "python", "-OO", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "binny_buddy.django_project.wsgi:application" ]