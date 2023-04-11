from email.message import Message
from email.header import decode_header
from bs4 import BeautifulSoup
import quopri
from typing import Union


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


def extract_email_subject(subject: Union[str, None]) -> str:
    """
    Extracts the subject from an email message.

    Args:
        subject (Union[str, None]): The subject of the email message. If None,
        returns 'Empty subject'.

    Returns:
        str: The subject of the email message as a string, or 'Empty subject' if
        subject is None.
    """
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
