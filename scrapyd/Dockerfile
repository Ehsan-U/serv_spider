# Build an egg of your project.

FROM python:3.10-slim AS build-stage

RUN pip install --no-cache-dir scrapyd-client

WORKDIR /usr/src/scrapyd

COPY . .

RUN scrapyd-deploy --build-egg=zcrawler.egg


# Build the image.

FROM python:3.10-slim

RUN mkdir -p /src/eggs/zcrawler

COPY --from=build-stage /usr/src/scrapyd/zcrawler.egg /src/eggs/zcrawler/1.egg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scrapyd.conf /etc/scrapyd/

EXPOSE 6800

ENTRYPOINT ["scrapyd", "--pidfile="]