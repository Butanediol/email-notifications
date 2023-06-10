from email.message import Message
from helpers.strings import *
import html2text

def extract_summary_from_plaintext(message: Message) -> str | None:
  """
  Extracts the email summary from a given message object.
  """

  summary = ''

  for part in message.walk():
    if part.get_content_type() == 'text/plain':
      charset = part.get_content_charset() or 'utf-8'
      summary += part.get_payload(decode=True).decode(charset)

  return summary == '' and None or summary

def extract_summary_from_html(message: Message) -> str | None:
  """
  Extracts the plaintext HTML content from a given message object.
  """

  summary = ''

  for part in message.walk():
    if part.get_content_type() == 'text/html':
      charset = part.get_content_charset() or 'utf-8'
      html = part.get_payload(decode=True).decode(charset)
      h = html2text.HTML2Text()
      h.body_width = 0
      h.ignore_tables = True
      h.ignore_images = True
      h.use_automatic_links = True
      summary += h.handle(data=html)

  return summary.strip() == '' and None or summary

def get_email_summary(message: Message) -> str:
  """
  Retrieve email body from a Message object and return it as a string.

  Args:
    message (Message): A Message object containing email message.

  Returns:
    str: The retrieved email body as a string.
  """
  # Get summary
  summary = extract_summary_from_plaintext(message=message) or extract_summary_from_html(message=message) or ''
  summary = compact_string(summary)

  return summary

def extract_email_subject(message: Message) -> str:
  """
  Extract the email subject from a given message object.

  Args:
    message (Message): An email message object.

  Returns:
    str: The extracted email subject. If the message object does not have a subject or the subject cannot be 
       decoded, returns 'Empty subject' or the original subject string respectively.
  """
  subject = message['Subject']
  if subject is None:
    return 'Empty subject'

  try:
    subjects = [subj[0].decode(subj[1] or 'utf-8')
          for subj in decode_header(subject)]
    return ' '.join(subjects)
  except AttributeError:
    return subject

def extract_email_attachment(message: Message) -> list[tuple[str, bytes]]:
  """
  Extract all email attachments from a given `email.message.Message` object.

  Args:
    message (Message): The email message to extract attachments from.

  Returns:
    A list of tuples, where each tuple contains the name and content of an extracted attachment.
    Each attachment is represented by a tuple containing its filename (as a string) and
    its content (as bytes).

  Notes:
    If an attachment's filename cannot be determined, it is given the default name 'Untitled attachment'.
    Normally, the max size of an email attachment is no larger than 50MB.
  """
  attachments: list[tuple[str, bytes]] = []

  for part in message.walk():
    if part.get_content_disposition() == 'attachment':
      filename = decode_header_string(part.get_filename('Untitled attachment'))
      file = part.get_payload(decode=True)
      attachments.append((filename, file))

  return attachments