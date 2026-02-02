import time
import os
import logging

from dotenv import load_dotenv
load_dotenv()

from Senders import get_senders
from mailbot import Mailbox
from random import randint

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s \t %(levelname)s \t %(message)s')
interval = int(os.environ.get('INTERVAL', '30'))

mailbox = Mailbox()
senders = get_senders()

logging.info('Sleep random time to avoid multiple instances running at the same time.')
time.sleep(randint(0, interval))

logging.info('Start checking...')
while (1):
    for email in mailbox.getUnseenMails():
        for sender in senders:
            sender.send(message=email)
    time.sleep(interval)