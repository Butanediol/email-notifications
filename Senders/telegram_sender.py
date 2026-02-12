from telebot import TeleBot
from telebot.types import MessageEntity
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

# Patterns produced by html2text:
#   [display text](url)  — named links
#   <url>                 — automatic links (text == url)
# Also match bare URLs not already inside markdown syntax.
_MARKDOWN_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_ANGLE_LINK_RE = re.compile(r'<(https?://[^>]+)>')
_BARE_URL_RE = re.compile(r'(?<!\()(https?://[^\s)\]>]+)')


def _utf16_len(text: str) -> int:
  """Return length of text in UTF-16 code units (as required by Telegram)."""
  return len(text.encode('utf-16-le')) // 2


def _build_message_with_entities(
  sender: str, to: str, subject: str, body: str
) -> tuple[str, list[MessageEntity]]:
  """Build plain text and a list of MessageEntity objects.

  URLs in the body are replaced with short display text and represented
  as text_link entities, so the full URL does not consume characters in
  the 4096-char text limit.
  """
  entities: list[MessageEntity] = []

  # --- Process body: replace links with display text, collect (offset_in_body, length, url) ---
  link_entities: list[tuple[int, int, str]] = []  # (offset_in_processed_body, utf16_len, url)

  def _replace_markdown_links(body_text: str) -> str:
    """Replace [text](url) with just text, recording entities."""
    result = ''
    last_end = 0
    for m in _MARKDOWN_LINK_RE.finditer(body_text):
      result += body_text[last_end:m.start()]
      display = m.group(1)
      url = m.group(2)
      offset_in_body = _utf16_len(result)
      length = _utf16_len(display)
      link_entities.append((offset_in_body, length, url))
      result += display
      last_end = m.end()
    result += body_text[last_end:]
    return result

  def _replace_angle_links(body_text: str) -> str:
    """Replace <url> with 'Link', recording entities."""
    result = ''
    last_end = 0
    for m in _ANGLE_LINK_RE.finditer(body_text):
      result += body_text[last_end:m.start()]
      url = m.group(1)
      display = 'Link'
      offset_in_body = _utf16_len(result)
      length = _utf16_len(display)
      link_entities.append((offset_in_body, length, url))
      result += display
      last_end = m.end()
    result += body_text[last_end:]
    return result

  def _replace_bare_urls(body_text: str) -> str:
    """Replace bare https?://... URLs with 'Link', recording entities."""
    result = ''
    last_end = 0
    for m in _BARE_URL_RE.finditer(body_text):
      result += body_text[last_end:m.start()]
      url = m.group(1)
      display = 'Link'
      offset_in_body = _utf16_len(result)
      length = _utf16_len(display)
      link_entities.append((offset_in_body, length, url))
      result += display
      last_end = m.end()
    result += body_text[last_end:]
    return result

  # Process links in order: markdown links first, then angle bracket, then bare URLs
  processed_body = _replace_markdown_links(body)
  processed_body = _replace_angle_links(processed_body)
  processed_body = _replace_bare_urls(processed_body)

  # --- Build the full text with header ---
  header_line1 = f'{sender} → {to}'
  header_line2 = subject
  text = f'{header_line1}\n{header_line2}\n\n{processed_body}'

  # --- Truncate if needed ---
  if _utf16_len(text) > _MAX_MESSAGE_LENGTH:
    # Truncate in a UTF-16 safe way
    ellipsis = '...'
    max_len = _MAX_MESSAGE_LENGTH - _utf16_len(ellipsis)
    # Trim characters until we fit
    while _utf16_len(text) > max_len:
      text = text[:-1]
    text += ellipsis

  # --- Build entities for bold header ---
  offset = 0
  # Bold: sender → to
  entities.append(MessageEntity(
    type='bold', offset=offset, length=_utf16_len(header_line1)
  ))
  offset += _utf16_len(header_line1) + _utf16_len('\n')  # skip newline

  # Bold: subject
  entities.append(MessageEntity(
    type='bold', offset=offset, length=_utf16_len(header_line2)
  ))

  # --- Adjust link entity offsets (they were relative to body, shift by header length) ---
  header_prefix = f'{header_line1}\n{header_line2}\n\n'
  header_offset = _utf16_len(header_prefix)
  text_utf16_len = _utf16_len(text)

  for body_offset, length, url in link_entities:
    abs_offset = header_offset + body_offset
    # Skip entities that fall beyond the truncated text
    if abs_offset + length > text_utf16_len:
      continue
    entities.append(MessageEntity(
      type='text_link', offset=abs_offset, length=length, url=url
    ))

  return text, entities


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
    text, entities = _build_message_with_entities(sender, to, subject, body)

    self.__bot.send_message(
      chat_id=self.__chat_id,
      text=text,
      entities=entities,
      disable_web_page_preview=True
    )
    logging.info(f'Telegram: {sender} -> {to}')

    for filename, file in extract_email_attachment(message):
      bytes_io = io.BytesIO(file)
      bytes_io.name = filename
      self.__bot.send_document(chat_id=self.__chat_id, document=bytes_io)
      logging.info(f'Telegram attachment: {filename}')
