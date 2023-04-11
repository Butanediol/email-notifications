from telebot import TeleBot
from email.message import Message
from helpers import *
import logging


class TelegramSender:
  
  def __init__(self, token: str, chatId: int | str):
    if not token:
      raise Exception('Missing Telegram token.')
    if not chatId:
      raise Exception('Missing Telegram chat ID.')
    self.__bot = TeleBot(token=token)
    self.__chatId = chatId

  def send(self, message: Message):
    text = """
    {sender} -> {to}
    {subject}
    {body}
    """.format(
        sender=extract_email_address(message['From']),
        to=extract_email_address(message['To']),
        subject=extract_email_subject(message),
        body=extract_email_body(message)
    )
    self.__bot.send_message(chat_id=self.__chatId, text=text)
    logging.info('Telegram: {sender} -> {to}'.format(sender=extract_email_address(message['From']), to=extract_email_address(message['To'])))
