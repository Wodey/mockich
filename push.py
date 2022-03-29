# This script is for our internal use, we will use this script
# to send message to any user by his chatID and we will use it to 
# send information about his match and google meet link

import sys
import requests

def sendMessage(token, chatId, msg):
    url = "https://api.telegram.org/bot{t}/sendMessage?chat_id={c}&text={m}".format(t=token, c=chatId, m=msg)
    requests.post(url)

token = input("Enter bot token: ")
chat_id = input("Enter chat ID: ")
message = input("Enter message to sent: ")

sendMessage(token, chat_id, message)