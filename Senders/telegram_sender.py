from telebot import TeleBot
from email.message import Message
from helpers.misc import retry
from helpers.messages import *
from helpers.strings import *
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
      body=get_email_summary(message)
    )
    text = remove_excessive_newlines(text)
    text = strip_leading_and_trailing_spaces(text)
    text = truncate_string(text)

    # Try to send message with markdown enabled
    try:
      self.__bot.send_message(chat_id=self.__chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
      self.__bot.send_message(chat_id=self.__chat_id, text=text, disable_web_page_preview=True)
      logging.error(f'{e}')
    

    logging.info('Telegram: {sender} -> {to}'.format(sender=extract_email_address(message['From']), to=extract_email_address(message['To'])))
    for filename, file in extract_email_attachment(message):
      bytes_io = io.BytesIO(file)
      bytes_io.name = filename
      self.__bot.send_document(chat_id=self.__chat_id, document=bytes_io)
      logging.info('Telegram: {filename}'.format(filename=filename))
