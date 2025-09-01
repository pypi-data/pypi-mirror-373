FROM python:3.12-slim-trixie


WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

ADD . /app

RUN uv  sync --locked
RUN apt-get update
RUN apt-get install wl-clipboard -y
RUN apt-get install tesseract-ocr -y
RUN apt-get install libtesseract-dev -y


ENTRYPOINT ["uv", "run", "img2text"]
CMD []
