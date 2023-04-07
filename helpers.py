from email.message import Message
from email.header import decode_header
from bs4 import BeautifulSoup
import quopri


def getEmailBody(message: Message, trimmed: bool = True) -> str:
    # Get body
    body = ''
    for part in message.walk():
        if part.get_content_type() == 'text/plain':
            body += part.get_payload(decode=True).decode() + '\n'
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

def decodeMailSubject(subject: str) -> str:
    try:
        subjects = [subj[0].decode(subj[1]) for subj in decode_header(subject)]
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