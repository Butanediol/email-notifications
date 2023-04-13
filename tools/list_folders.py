import imaplib
import os

mailServer = os.environ['IMAP_MAIL_SERVER']
mailAddress = os.environ['IMAP_MAIL_USERNAME']
mailPassword = os.environ['IMAP_MAIL_PASSWORD']

imap = imaplib.IMAP4_SSL(mailServer)
imap.login(mailAddress, mailPassword)

for folder in imap.list()[1]:
	print(folder.decode('utf-8'))

# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_LOGIN=n872485238@gmail.com
# SMTP_PASSWORD=xgrwbrweqskfelht