from email.message import Message
from email.header import decode_header
from bs4 import BeautifulSoup
import quopri
import time
import logging


def replace_consecutive_newlines(text: str) -> str:
  """
  Replaces three or more consecutive newline characters with two newline characters in the given text string.

  Args:
    text (str): A string containing newline characters.

  Returns:
    str: The modified text string with three or more consecutive newlines replaced by two newlines.
  """

  while '\n\n\n' in text:
    text = text.replace('\n\n\n', '\n\n')
  return text

def remove_leading_spaces(text):
  """
  Removes leading spaces from each line of the input text.

  Args:
  text (str): The text to remove leading spaces from.

  Returns:
  str: The input text with leading spaces removed from each line.
  """
  lines = text.split('\n')
  for i in range(len(lines)):
    lines[i] = lines[i].strip()
  return '\n'.join(lines)

def extract_email_body(message: Message) -> str:
  """
  Retrieve email body from a Message object and return it as a string.

  Args:
    message (Message): A Message object containing email message.

  Returns:
    str: The retrieved email body as a string.
  """
  # Get body
  body = ''
  for part in message.walk():
    charset = part.get_content_charset() or 'utf-8'
    if part.get_content_type() == 'text/plain':
      body += part.get_payload(decode=True).decode(charset) + '\n'
      break
    elif part.get_content_type() == 'text/html':
      try:
        html = quopri.decodestring(part.get_payload()).decode()
      except Exception as _:
        html = part.get_payload()
      body += BeautifulSoup(html, 'html.parser').text

  body = replace_consecutive_newlines(body)
  body = remove_leading_spaces(body)

  # Trim body if too long
  if len(body) > 1000:
    body = body[:1000] + '...'
  return body


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


def extract_email_address(address: str) -> str:
  """
  Extracts the email address from a given string.

  Args:
    address (str): A string containing an email address in the format "Name <email@address.com>" or just "email@address.com".

  Returns:
    str: The extracted email address.
  """
  try:
    sender_email = address.split('<')[1].split('>')[0]
  except IndexError:
    sender_email = address
  return sender_email

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

def decode_header_string(header_string: str) -> str:
  """
  Decode a given header string using the email library's `decode_header()` function.

  Args:
    header_string (str): The header string to be decoded.

  Returns:
    A decoded version of the header string, if the decoding was successful.
    Otherwise, the original header string is returned.

  Raises:
    IndexError: If `decode_header()` function does not return any decoded strings.
      In this case, the function logs the error and returns the original header string.
  """
  try:
    decoded, _ = decode_header(header_string)[0]
    if type(decoded) is bytes:
      return decoded.decode()
    else:
      return header_string
  except IndexError as e:
    logging.error(e)
    return header_string

def retry(max_tries:int=3, expnential_backoff_c=1):
  """
  A decorator that provides a mechanism for retrying a function in case of exceptions.

  Args:
    max_tries (int): Maximum number of times the decorated function is allowed to be retried.
      Default value is 3.
    expnential_backoff_c (int/float): The factor by which the delay between retries is increased on each
      subsequent retry attempt. Default value is 1, meaning there will be no exponential backoff.

  Returns:
    A decorator that wraps the passed-in function, providing a mechanism for retrying it in case of exceptions.

  Example usage:
    @retry(max_tries=5, expnential_backoff_c=2)
    def foo():
      # function implementation
  """
  def decorator(func):
    def wrapper(*args, **kwargs):
      delay = 1
      for _ in range(max_tries):
        try:
          return func(*args, **kwargs)
        except Exception as e:
          print(f"Exception caught: {e}")
          time.sleep(delay)
          delay *= expnential_backoff_c
      raise Exception("Failed after multiple retries.")
    return wrapper
  return decorator