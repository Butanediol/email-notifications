import time
import os
import logging

from Senders.telegram_sender import TelegramSender
from Senders.bark_sender import BarkSender
from mailbot import Mailbox
from random import randint

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s \t %(levelname)s \t %(message)s')
interval = int(os.environ.get('INTERVAL', '30'))

mailbox = Mailbox()
telegram = TelegramSender()
bark = BarkSender()

# Sleep random time to avoid multiple instances running at the same time.
time.sleep(randint(0, interval))

logging.info('Start checking...')
while (1):
    for email in mailbox.getUnseenMails():
        telegram.send(message=email)
        bark.send(message=email)
    time.sleep(interval)