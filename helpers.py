from email.message import Message
import base64


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

def decodeMailSubject(subject: str):
    try:
        # Split the string into its components and extract the encoding method and text
        charset, encoding, encoded_text = subject.split('?')[1:4]
        # Decode the Base64-encoded text using the specified character set
        decoded_bytes = base64.b64decode(encoded_text)
        decoded_text = decoded_bytes.decode(charset)
        return decoded_text
    except (ValueError, UnicodeDecodeError):
        # Return the original subject line if decoding failed
        return subject