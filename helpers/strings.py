from email.header import decode_header
from typing import Optional
import logging
import re

def compact_string(text: str) -> str:
  """
  Make input more compact.

  Args:
    text (str): The string to remove whitespace characters from.

  Returns:
    str: The input string with all whitespace characters removed.
  """
  return strip_leading_and_trailing_spaces(remove_excessive_newlines(strip_leading_and_trailing_spaces(text)))


def remove_excessive_newlines(text: str) -> str:
  """
  Remove excessive newlines from the given text.

  Args:
      text (str): The input text containing newlines.

  Returns:
      str: The text with excessive newlines removed.
  """

  while '\n\n\n' in text:
    text = text.replace('\n\n\n', '\n\n')
  return text

def strip_leading_and_trailing_spaces(text: str):
  """
  Removes leading and trailing spaces from each line in the given text.

  Args:
      text (str): The text to process.

  Returns:
      str: The processed text with leading and trailing spaces removed from each line.
  """
  lines = text.split('\n')
  for i in range(len(lines)):
    lines[i] = lines[i].strip()
  return '\n'.join(lines)

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