FROM python:3.10

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

ENV BOT_TOKEN=5168967834:AAH-Dv5cIpc6A4Z3udX8R3MT1xcEB_Rki9U
COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","main.py"]