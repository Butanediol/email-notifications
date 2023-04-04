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
        # Get sender email address
        sender_email = email['From'].split('<')[1].split('>')[0]

        body = helpers.getEmailBody(email)

        # Get Subject
        subject = helpers.decodeMailSubject(str(email['Subject']))

        data = str(sender_email) + '\n' + subject + '\n' + str(body)
        telegram.send(data)
        bark.send(title=str(email['To']), content=str(body))

    time.sleep(30)
