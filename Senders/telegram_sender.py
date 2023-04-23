from telebot import TeleBot
from email.message import Message
from helpers import *
from os import environ
import io
import logging


class TelegramSender:
  
  def __init__(self):
    self.__chat_id = environ['TELEGRAM_CHAT_ID']
    self.__tg_bot_token = environ['TELEGRAM_BOT_TOKEN']
    self.__bot = TeleBot(token=self.__tg_bot_token)

  @retry(max_tries=20)
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
    self.__bot.send_message(chat_id=self.__chat_id, text=text, disable_web_page_preview=True)
    logging.info('Telegram: {sender} -> {to}'.format(sender=extract_email_address(message['From']), to=extract_email_address(message['To'])))
    for filename, file in extract_email_attachment(message):
      bytes_io = io.BytesIO(file)
      bytes_io.name = filename
      self.__bot.send_document(chat_id=self.__chat_id, document=bytes_io)
      logging.info('Telegram: {filename}'.format(filename=filename))
