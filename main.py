import mailbot
import time
import os
import logging

from Senders.telegram_sender import TelegramSender
from Senders.bark_sender import BarkSender

chatId = os.environ['TELEGRAM_CHAT_ID']
tgApiToken = os.environ['TELEGRAM_BOT_TOKEN']
mailServer = os.environ['IMAP_MAIL_SERVER']
mailAddress = os.environ['IMAP_MAIL_USERNAME']
mailPassword = os.environ['IMAP_MAIL_PASSWORD']
mailFolder = os.environ['IMAP_MAIL_FOLDER']
barkToken = os.environ['BARK_TOKEN']

logging.basicConfig(level=logging.INFO, format='%(asctime)s \t %(levelname)s \t %(message)s')

mailbox = mailbot.Mailbox(mailServer, mailAddress, mailPassword, mailFolder)

telegram = TelegramSender(token=tgApiToken, chatId=chatId)
bark = BarkSender(token=barkToken)

logging.info('Start checking...')
while (1):
    logging.debug('Checking...')
    emails = mailbox.getUnseenMails(False)

    for email in emails:
        telegram.send(message=email)
        bark.send(message=email)

    time.sleep(30)
