from email.message import Message
from os import environ
import imaplib
import email.header
import logging

# Some Concepts:
#   Each mail has a unique identifier (UID).
#   To fetch mails we first have to use UID commands 
#     to get the UIDs of the mails we want to fetch. (UID SEARCH [UNSEEN \ ALL])

class Mailbox:
  def __init__(self):
    self.__mail_server = environ['IMAP_MAIL_SERVER']
    self.__mail_username = environ['IMAP_MAIL_USERNAME']
    self.__mail_password = environ['IMAP_MAIL_PASSWORD']
    self.__mail_folder = environ.get('IMAP_MAIL_FOLDER', 'INBOX')
    self.__mail_remains_unread = environ.get('IMAP_MAIL_REMAINS_UNREAD', 'true').lower() == 'true'
    self.__login()
    
  def __login(self):
    """
      Log in mail account.
      Set last mail UID to the highest mail UID.
    """
    try:
      self.__imap = imaplib.IMAP4_SSL(self.__mail_server)
      self.__imap.login(self.__mail_username, self.__mail_password)
      uids = self.__get_uids()

      # Last UID is the UID with the highest value. 
      self.__lastUid = max(uids) if len(uids) > 0 else -1
    except:
      logging.critical('Access denied. Check the data or the server permissions.')
      exit(1)
    
  def getUnseenMails(self) -> list[Message]:
    """
    Get unseen mails.
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
        mails.append(message)
        if self.__mail_remains_unread: self.__mark_as_unread(uid)
      except:
        continue
    
    if len(uids) > 0:
      self.__lastUid = max(uids)
    
    return mails

  def __get_uids(self) -> list[int]:
    """
      Get mail uids.
    """
    try:
      self.__imap.select(self.__mail_folder)

      # Get all mail UIDs.
      _, uids = self.__imap.uid('SEARCH', "ALL")
      uids = [int(uid) for uid in uids[0].split()]
    except AttributeError as e:
      logging.debug(f'Error while checking new emails: {e} \t Check out GitHub Wiki.')
      return []
    except Exception as e:
      logging.error(f'Error while checking new emails: {e} \t Re-login and try again.')
      self.__login()
      return []
    else:
      logging.debug('All UIDs: ' + str(uids))
      return list(uids)

  def __mark_as_unread(self, uid: int):
    """
      Mark mail as unread.
    """
    logging.info(f'Mark mail {uid} as unread.')
    try:
      self.__imap.uid('STORE', str(uid), '-FLAGS', '(\\SEEN)')
    except Exception as e:
      logging.error(f'Error while marking mail {uid} as unread: {e}')