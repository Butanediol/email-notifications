import mailbot
import helpers
import time
import os

chatId = os.environ['TELEGRAM_CHAT_ID']
tgApiToken = os.environ['TELEGRAM_BOT_TOKEN']
mailServer = os.environ['IMAP_MAIL_SERVER']
mailAddress = os.environ['IMAP_MAIL_USERNAME']
mailPassword = os.environ['IMAP_MAIL_PASSWORD']
mailFolder = os.environ['IMAP_MAIL_FOLDER']
barkToken = os.environ['BARK_TOKEN']

mailbox = mailbot.Mailbox(mailServer, mailAddress, mailPassword, mailFolder)
telegram = mailbot.TgSender(tgApiToken, chatId)
bark = mailbot.BarkSender(token=barkToken)

print('Start checking..')
while (1):
    emails = mailbox.getUnseenMails(False)

    for email in emails:
        sender_email = helpers.getEmailSender(email)
        body = helpers.getEmailBody(email)
        subject = helpers.decodeMailSubject(email['Subject'])

        data = 'From: ' + sender_email + '\n\n' + subject + '\n\n' + body
        telegram.send(data)
        bark.send(title='From: ' + sender_email, content=subject)

    time.sleep(30)
