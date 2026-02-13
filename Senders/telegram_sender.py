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

# Patterns produced by html2text
_MARKDOWN_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_ANGLE_LINK_RE = re.compile(r'<(https?://[^>]+)>')
_BARE_URL_RE = re.compile(r'(?<!\()(https?://[^\s)\]>*\x00]+)')
_BOLD_RE = re.compile(r'\*\*(.+?)\*\*', re.DOTALL)
_ITALIC_RE = re.compile(r'(?<![*\w])_(.+?)_(?![*\w])')

# Sentinel character used to mark entity boundaries in intermediate text.
# All regex substitutions insert sentinel-wrapped tags; a single final scan
# strips them and extracts entity offsets — no cross-pass offset adjustment.
_S = '\x00'
_TAG_RE = re.compile(r'\x00([BE]\d+)\x00')


def _utf16_len(text: str) -> int:
  """Return length of text in UTF-16 code units (as required by Telegram)."""
  return len(text.encode('utf-16-le')) // 2


def _process_body(body: str) -> tuple[str, list[MessageEntity]]:
  """Replace links and formatting markers in body with Telegram entities.

  Uses sentinel tokens so that all regex passes simply insert markers,
  and entity offsets are computed in one final scan of the result.
  """
  meta: list[tuple[str, str | None]] = []  # indexed by entity id: (type, url)

  def _mark(content: str, etype: str, url: str | None = None) -> str:
    eid = len(meta)
    meta.append((etype, url))
    return f'{_S}B{eid}{_S}{content}{_S}E{eid}{_S}'

  def _md_link(m):
    display, url = m.group(1), m.group(2)
    if re.match(r'https?://', display):
      display = 'Link'
    return _mark(display, 'text_link', url)

  # Replace links (markdown first, then angle brackets, then bare URLs)
  text = _MARKDOWN_LINK_RE.sub(_md_link, body)
  text = _ANGLE_LINK_RE.sub(lambda m: _mark('Link', 'text_link', m.group(1)), text)
  text = _BARE_URL_RE.sub(lambda m: _mark('Link', 'text_link', m.group(1)), text)

  # Replace formatting markers
  text = _BOLD_RE.sub(lambda m: _mark(m.group(1), 'bold'), text)
  text = _ITALIC_RE.sub(lambda m: _mark(m.group(1), 'italic'), text)

  # Single scan: strip sentinel tags, build plain text + entities
  parts = _TAG_RE.split(text)  # alternates: [text, tag, text, tag, ..., text]
  result_parts: list[str] = []
  utf16_pos = 0
  open_ents: dict[int, int] = {}
  entities: list[MessageEntity] = []

  for i, part in enumerate(parts):
    if i % 2 == 0:
      result_parts.append(part)
      utf16_pos += _utf16_len(part)
    else:
      eid = int(part[1:])
      if part[0] == 'B':
        open_ents[eid] = utf16_pos
      else:
        start = open_ents.pop(eid)
        etype, url = meta[eid]
        entities.append(MessageEntity(
          type=etype, offset=start, length=utf16_pos - start, url=url
        ))

  return ''.join(result_parts), entities


def _build_message_with_entities(
  sender: str, to: str, subject: str, body: str
) -> tuple[str, list[MessageEntity]]:
  """Build plain text + entity list for a Telegram message."""
  processed_body, body_entities = _process_body(body)

  header_line1 = f'{sender} → {to}'
  header_line2 = subject
  text = f'{header_line1}\n{header_line2}\n\n{processed_body}'

  # Truncate if needed
  if _utf16_len(text) > _MAX_MESSAGE_LENGTH:
    ellipsis = '...'
    max_len = _MAX_MESSAGE_LENGTH - _utf16_len(ellipsis)
    while _utf16_len(text) > max_len:
      text = text[:-1]
    text += ellipsis

  # Header bold entities
  entities: list[MessageEntity] = [
    MessageEntity(type='bold', offset=0, length=_utf16_len(header_line1)),
    MessageEntity(type='bold', offset=_utf16_len(header_line1) + 1, length=_utf16_len(header_line2)),
  ]

  # Shift body entities by header length and keep those within bounds
  header_offset = _utf16_len(f'{header_line1}\n{header_line2}\n\n')
  text_utf16_len = _utf16_len(text)
  for ent in body_entities:
    ent.offset += header_offset
    if ent.offset + ent.length <= text_utf16_len:
      entities.append(ent)

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
