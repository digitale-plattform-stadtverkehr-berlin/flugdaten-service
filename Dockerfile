FROM python:3-alpine

WORKDIR /usr/src/app

ENV DOWNLOAD_URL https://aoe.berlin-airport.de/download/viz/BER_VMZ.dat
ENV DOWNLOAD_USER ""
ENV DOWNLOAD_PW ""

ENV HOST localhost
ENV PORT 8000

ENV LOG_LEVEL INFO


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY flugdaten_api.py .

CMD [ "python", "-u", "flugdaten_api.py"]
