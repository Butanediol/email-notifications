from email.message import Message
import imaplib
import email.header
import logging

# Some Concepts:
#   Each mail has a unique identifier (UID).
#   To fetch mails we first have to use UID commands 
#     to get the UIDs of the mails we want to fetch. (UID SEARCH [UNSEEN \ ALL])

class Mailbox:
  def __init__(self, mail: str, mailbox: str, password: str, folder: str = 'Inbox'):
    if not mail or not mailbox or not password:
      raise Exception('Each parameter must not be empty') 
    self.mail = mail
    self.mailbox = mailbox
    self.__password = password
    self.folder = folder
    self.__login()
    
  def __login(self):
    """
      Log in mail account.
      Set last mail UID to the highest mail UID.
    """
    try:
      self.__imap = imaplib.IMAP4_SSL(self.mail)
      self.__imap.login(self.mailbox, self.__password)
      uids = self.__get_uids()

      # Last UID is the UID with the highest value. 
      self.__lastUid = max(uids) if len(uids) > 0 else -1
    except:
      raise Exception('Access denied. Check the data or the server permissions.')
    
  def getUnseenMails(self) -> list[Message]:
    """
    Get unseen mails.

    :param allUnread: If true, get all unread mails. Otherwise, get only unread mails after the last UID.
    """
    uids = [uid for uid in self.__get_uids() if uid > self.__lastUid]
    logging.debug('Unseen UIDs: ' + str(uids))

    if len(uids) == 0:
      return []
    
    mails: list[Message] = []
    for uid in uids:
      try:
        _, body = self.__imap.uid('fetch', str(uid), 'BODY[]')
        message = email.message_from_bytes(body[0][1])
      except:
        continue
      else:
        mails.append(message)
    
    if len(uids) > 0:
      self.__lastUid = max(uids)
    
    return mails

  def __get_uids(self) -> list[int]:
    """
      Get mail uids.
    """
    try:
      self.__imap.select(self.folder)

      # Get all mail UIDs.
      _, uids = self.__imap.uid('SEARCH', "ALL")
      uids = [int(uid) for uid in uids[0].split()]
    except:
      return []
    else:
      logging.debug('All UIDs: ' + str(uids))
      return list(uids)