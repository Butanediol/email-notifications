from email.message import Message
from helpers.misc import retry
from helpers.messages import *
from Senders.base import BaseSender
from os import environ
import requests
import json
import logging

# Gmail https://img.butanediol.me/51/a9c92d6ec0446833c947e722628d0585f7e34d.png
# iCloud https://img.butanediol.me/40/0ef6043445bc21886531ffce6ed97a8da8c143.png

class BarkSender(BaseSender):

  @classmethod
  def enabled(cls) -> bool:
    return 'BARK_TOKEN' in environ

  def __init__(self):
    self.__bark_token = environ['BARK_TOKEN']
    self.__bark_server = environ.get('BARK_SERVER', 'https://api.day.app')
    self.__bark_group = environ.get('BARK_GROUP', 'Email')
    self.__bark_icon = environ.get('BARK_ICON', 'https://img.butanediol.me/99/f651c5840b88226f6aa5b9cd6398e85deed6e6.png')
    self.__sendMessageUrl = self.__bark_server + '/' + self.__bark_token

  @retry(max_tries=20)
  def send(self, message: Message):
    content = get_email_summary(message=message)
    title = extract_email_subject(message=message)
    try:
      requests.post(
        url=self.__sendMessageUrl,
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "body": content,
            "group": self.__bark_group,
            "title": title,
            "icon": self.__bark_icon,
        }),
        )
      logging.info(f'Bark: {title}')
    except requests.exceptions.RequestException:
      logging.error('HTTP Request failed')