import mailbot
import time
import os
import logging

from Senders.telegram_sender import TelegramSender
from Senders.bark_sender import BarkSender

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper(), format='%(asctime)s \t %(levelname)s \t %(message)s')

mailbox = mailbot.Mailbox()

telegram = TelegramSender()
bark = BarkSender()

logging.info('Start checking...')
while (1):
    logging.debug('Checking...')
    emails = mailbox.getUnseenMails()
    if emails.__len__() != 0:
        logging.debug('Found %d emails' % emails.__len__())

    for email in emails:
        telegram.send(message=email)
        bark.send(message=email)

    time.sleep(30)
