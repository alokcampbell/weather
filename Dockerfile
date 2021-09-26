FROM python:3.8-buster

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install curl -y
RUN curl -s https://install.speedtest.net/app/cli/install.deb.sh | bash
RUN apt-get install speedtest -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./pi_report.py" ]