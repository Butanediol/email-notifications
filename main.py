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
        sender_address = helpers.extract_email_address(email['From'])
        receiver_address = helpers.extract_email_address(email['To'])
        body = helpers.extract_email_body(email)
        subject = helpers.extract_email_subject(email['Subject'])

        data = sender_address + ' -> ' + receiver_address + '\n\n' + subject + '\n\n' + body
        telegram.send(data)
        bark.send(title='From: ' + sender_address, content=subject)

    time.sleep(30)
