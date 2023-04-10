from email.message import Message
from email.header import decode_header
from bs4 import BeautifulSoup
import quopri
from typing import Union


def getEmailBody(message: Message) -> str:
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
            except Exception as e:
                html = part.get_payload()
            body += BeautifulSoup(html, 'html.parser').text

    # Replace multiple white space characters with only one
    body = ' '.join(body.split())

    # Trim body if too long
    if len(body) > 1000:
        body = body[:1000] + '...'
    return body

def decodeMailSubject(subject: Union[str, None]) -> str:

    if subject is None:
        return 'Empty subject'

    try:
        subjects = [subj[0].decode(subj[1] or 'utf-8') for subj in decode_header(subject)]
        return ' '.join(subjects)
    except AttributeError:
        return subject

def getEmailAddress(address: str) -> str:
    # Get sender email address
    try:
        sender_email = address.split('<')[1].split('>')[0]
    except IndexError:
        sender_email = address
    return sender_email