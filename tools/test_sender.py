"""
Send a test notification through all enabled senders without needing real email.

Usage:
    python tools/test_sender.py
    python tools/test_sender.py --from "alice@example.com" --to "bob@example.com" --subject "Hello" --body "Test body"
"""
import argparse
import logging
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from email.mime.text import MIMEText

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Senders import get_senders


def build_test_message(sender: str, to: str, subject: str, body: str) -> MIMEText:
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    return msg


def main():
    parser = argparse.ArgumentParser(description='Test notification senders with a fake email.')
    parser.add_argument('--from', dest='sender', default='test@example.com', help='From address')
    parser.add_argument('--to', default='you@example.com', help='To address')
    parser.add_argument('--subject', default='Test Email Notification', help='Email subject')
    parser.add_argument('--body', default='This is a test email sent by tools/test_sender.py to verify that senders are working correctly.', help='Email body')
    args = parser.parse_args()

    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s \t %(levelname)s \t %(message)s')

    senders = get_senders()
    if not senders:
        logging.warning('No senders are enabled. Check your environment variables.')
        return

    message = build_test_message(args.sender, args.to, args.subject, args.body)

    for sender in senders:
        name = sender.__class__.__name__
        logging.info(f'Sending test message via {name}...')
        try:
            sender.send(message=message)
            logging.info(f'{name}: OK')
        except Exception as e:
            logging.error(f'{name}: Failed - {e}')


if __name__ == '__main__':
    main()
