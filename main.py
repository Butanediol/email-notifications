import mailbot
import time
import os

chatId       = os.environ['TELEGRAM_CHAT_ID']
tgApiToken   = os.environ['TELEGRAM_BOT_TOKEN']
mailServer   = os.environ['IMAP_MAIL_SERVER']
mailAddress  = os.environ['IMAP_MAIL_USERNAME']
mailPassword = os.environ['IMAP_MAIL_PASSWORD']
mailFolder   = os.environ['IMAP_MAIL_FOLDER']
barkToken    = os.environ['BARK_TOKEN']

mailbox = mailbot.Mailbox(mailServer, mailAddress, mailPassword, mailFolder)
sender  = mailbot.TgSender(tgApiToken, chatId)
bark    = mailbot.BarkSender(token=barkToken)

print('Start checking..')
while(1):
  emails = mailbox.getUnseenMails(False)

  for email in emails:
    data = str(email['sender']) + '\n\n' + str(email['subject'])
    print(data)
    sender.send(data)
    bark.send(title=str(email['to']), content=str(email['subject']))

  time.sleep(30)
    
    
