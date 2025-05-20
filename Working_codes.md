# requirements

```
selenium==3.12.0
ipython==7.0.1
```

# Test code for selenium

```python

from selenium import webdriver
from time import sleep


class TestBooking(webdriver.Chrome):

    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        driver_path = '/usr/local/bin/chromedriver'
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(
            driver_path, options=chromeOptions)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        path = 'https://www.googleal.com/'
        self.base_url = path

    def tearDown(self):
        sleep(5)
        self.driver.quit()

    def test(self):
        print("Test method")
        self.driver.get('https://www.google.com/')
        print("#" * 50)
        print("https://www.google.com/----title-->>>>>: ", self.driver.title)
        print("#" * 50)


if __name__ == "__main__":
    booking = TestBooking()
    booking.test()
    booking.tearDown()

```

# Docker file

```dockerfile

FROM python:3


WORKDIR /srv


# ADD . /srv
RUN apt-get -y update
RUN pip install --upgrade pip
RUN apt-get install zip -y
RUN apt-get install unzip -y

COPY requirements.txt ./
RUN pip install -r requirements.txt


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


CMD ["python", "main_test.py"]

```

# Command to build docker image

```bash
sudo docker build . -t test_s_3 && sudo docker run -it -v .:/srv test_s_3 bash
```
