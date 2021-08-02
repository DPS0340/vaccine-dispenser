FROM python:latest

WORKDIR /code

COPY . .

RUN pip install -r requirements.txt

RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt update -y && apt install -y google-chrome-stable

ENV PYTHONPATH /code

CMD ["python", "/code/src/main.py"]