# FROM python:3

FROM nikolaik/python-nodejs:python3.8-nodejs14-slim


WORKDIR /app


# ADD . /srv
RUN apt-get -y update
RUN apt-get install curl -y
RUN pip install --upgrade pip
RUN apt-get install zip -y
RUN apt-get install unzip -y



COPY requirements.txt ./
COPY package*.json ./

RUN pip install -r requirements.txt
RUN npm install


# Install chromedriver
RUN wget -N https://chromedriver.storage.googleapis.com/72.0.3626.69/chromedriver_linux64.zip -P ~/
RUN unzip ~/chromedriver_linux64.zip -d ~/
RUN rm ~/chromedriver_linux64.zip
RUN mv -f ~/chromedriver /usr/local/bin/chromedriver
RUN chown root:root /usr/local/bin/chromedriver
RUN chmod 0755 /usr/local/bin/chromedriver


# Install chrome broswer
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable

EXPOSE 8008
