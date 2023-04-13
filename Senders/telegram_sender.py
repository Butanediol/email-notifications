import io
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
    text = replace_consecutive_newlines(text)
    text = remove_leading_spaces(text)
    self.__bot.send_message(chat_id=self.__chatId, text=text)
    logging.info('Telegram: {sender} -> {to}'.format(sender=extract_email_address(message['From']), to=extract_email_address(message['To'])))
    for filename, file in extract_email_attachment(message):
      bytes_io = io.BytesIO(file)
      bytes_io.name = filename
      self.__bot.send_document(chat_id=self.__chatId, document=bytes_io)
      logging.info('Telegram: {filename}'.format(filename=filename))
