FROM python:3.10
ENV TZ="Europe/Russia"

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

# cache results to avoid rebuilding the dependency everytime
ADD ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

ADD . /usr/src/app

# TODO: check if this is a best practice 
ENV BOT_TOKEN=5168967834:AAH-Dv5cIpc6A4Z3udX8R3MT1xcEB_Rki9U

CMD ["python", "-u" , "main.py"]
