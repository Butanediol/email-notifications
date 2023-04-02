from os.path import basename
import time
import os
import sys

sys.path.insert(0, '.')
from mailbot import Mailbox
from Senders.BarkSender import BarkSender
from Senders.TelegramSender import TgSender

chatId       = os.environ['TELEGRAM_CHAT_ID']
tgApiToken   = os.environ['TELEGRAM_BOT_TOKEN']
mailServer   = os.environ['IMAP_MAIL_SERVER']
mailAddress  = os.environ['IMAP_MAIL_USERNAME']
mailPassword = os.environ['IMAP_MAIL_PASSWORD']
mailFolder   = os.environ['IMAP_MAIL_FOLDER']
barkToken    = os.environ['BARK_TOKEN']
barkServer   = os.getenv('BARK_SERVER', 'https://api.day.app')
iconUrl      = os.getenv('ICON_URL', '')

mailbox = Mailbox(mail=mailServer, mailbox=mailAddress, password=mailPassword, folder=mailFolder)
telegram= TgSender(token=tgApiToken, chatId=chatId)
bark    = BarkSender(token=barkToken, baseUrl=barkServer)

print('Start checking..')
while(1):
  emails = mailbox.getUnseenMails(False)

  for email in emails:
    # Get sender email address
    sender_email = email['From'].split('<')[1].split('>')[0]

    # Get body
    body = ''
    for part in email.walk():
      if part.get_content_type() == 'text/plain':
        body = part.get_payload(decode=True).decode()
        break

    # Get Subject
    subject = email['Subject']

    data = str(sender_email) + '\n\n' + str(subject) + '\n\n' + str(body)
    telegram.send(data)
    bark.send(title=str(email['To']), content=str(body), icon=iconUrl)

  time.sleep(30)