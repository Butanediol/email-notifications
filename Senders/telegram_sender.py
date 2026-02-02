from telebot import TeleBot
from email.message import Message
from helpers.misc import retry
from helpers.messages import extract_email_attachment, extract_email_subject, get_email_summary
from helpers.strings import extract_email_address
from Senders.base import BaseSender
from os import environ
import io
import logging
import re

# Telegram message limit
_MAX_MESSAGE_LENGTH = 4096

# Characters that must be escaped in MarkdownV2 (outside code blocks)
_MARKDOWN_V2_SPECIAL = r'_*[]()~`>#+-=|{}.!\\'


def escape_markdown_v2(text: str) -> str:
  """Escape special characters for Telegram MarkdownV2 format."""
  return re.sub(r'([_*\[\]()~`>#+=|{}.!\\-])', r'\\\1', text)


class TelegramSender(BaseSender):

  @classmethod
  def enabled(cls) -> bool:
    return 'TELEGRAM_CHAT_ID' in environ and 'TELEGRAM_BOT_TOKEN' in environ

  def __init__(self):
    self.__chat_id = environ['TELEGRAM_CHAT_ID']
    self.__bot = TeleBot(token=environ['TELEGRAM_BOT_TOKEN'])

  def _format_message(self, message: Message) -> tuple[str, str, str, str]:
    """Extract and return (sender, to, subject, body) from email."""
    sender = extract_email_address(message['From'])
    to = extract_email_address(message['To'])
    subject = extract_email_subject(message)
    body = get_email_summary(message)
    return sender, to, subject, body

  @retry(max_tries=20)
  def send(self, message: Message):
    sender, to, subject, body = self._format_message(message)

    text = (
      f'*{escape_markdown_v2(sender)}* → *{escape_markdown_v2(to)}*\n'
      f'*{escape_markdown_v2(subject)}*\n\n'
      f'{escape_markdown_v2(body)}'
    )
    if len(text) > _MAX_MESSAGE_LENGTH:
      text = text[:_MAX_MESSAGE_LENGTH - 6] + '\\.\\.\\.'

    self.__bot.send_message(
      chat_id=self.__chat_id,
      text=text,
      parse_mode='MarkdownV2',
      disable_web_page_preview=True
    )
    logging.info(f'Telegram: {sender} -> {to}')

    for filename, file in extract_email_attachment(message):
      bytes_io = io.BytesIO(file)
      bytes_io.name = filename
      self.__bot.send_document(chat_id=self.__chat_id, document=bytes_io)
      logging.info(f'Telegram attachment: {filename}')
