from email.message import Message
from helpers import *
import requests
import json
import logging

class BarkSender:

  def __init__(self, token, baseUrl="https://api.day.app"):
    if not token:
      raise Exception('Missing Bark token.')
    self.__deviceToken = token
    self.__sendMessageUrl = baseUrl + '/' + token
    
  def send(self, message: Message):
    content = extract_email_subject(message=message)
    title = extract_email_address(message['From'])
    try:
      response = requests.post(
        url=self.__sendMessageUrl,
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "body": content,
            "group": "Email",
            "title": title,
            "badge": ""
        }),
        )
      logging.info('Bark: {title} - {content}'.format(title=title, content=content))
    except requests.exceptions.RequestException:
      logging.error('HTTP Request failed')