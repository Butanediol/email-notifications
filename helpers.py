from email.message import Message


def getEmailBody(message: Message, trimmed: bool = True) -> str:
    # Get body
    body = ''
    for part in message.walk():
        if part.get_content_type() == 'text/plain':
            body = part.get_payload(decode=True).decode()
            break

    # Replace multiple white space characters with only one
    body = ' '.join(body.split())

    # Trim body if too long
    if len(body) > 1000:
        body = body[:1000] + '...'
    return body
