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
    self.__imap = None
    self.__connect()
    self.__lastUid = self.__get_max_uid()

  def __connect(self):
    """
      Establish IMAP connection and authenticate.
      Raises on failure so callers can decide how to handle it.
    """
    self.__imap = imaplib.IMAP4_SSL(self.__mail_server)
    self.__imap.login(self.__mail_username, self.__mail_password)

  def __reconnect(self):
    """
      Re-establish IMAP connection after a failure.
    """
    logging.info('Reconnecting to IMAP server...')
    try:
      self.__connect()
      logging.info('Reconnected successfully.')
    except Exception as e:
      logging.error(f'Reconnect failed: {e}')
      raise

  def __ensure_connected(self):
    """
      Ensure we have a working IMAP connection.
      Try a NOOP to check; reconnect if it fails.
    """
    try:
      self.__imap.noop()
    except Exception:
      self.__reconnect()

  def getUnseenMails(self) -> list[Message]:
    """
    Get unseen mails since the last processed UID.
    Handles connection failures by reconnecting and retrying once.
    """
    try:
      self.__ensure_connected()
      uids = self.__get_uids()
    except Exception as e:
      logging.error(f'Error while fetching UIDs: {e}')
      return []

    uids = [uid for uid in uids if uid > self.__lastUid]
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
        # Advance lastUid per successfully processed email,
        # so a failure mid-batch doesn't skip earlier successes
        # or re-send them on the next poll.
        self.__lastUid = uid
      except Exception as e:
        logging.error(f'Error while fetching mail {uid}: {e}')
        # Stop processing this batch — connection is likely dead.
        # Successfully fetched mails are returned; remaining UIDs
        # (including this one) will be retried on the next poll
        # because lastUid was only advanced for successes.
        break

    return mails

  def __get_uids(self) -> list[int]:
    """
      Get all mail UIDs from the selected folder.
    """
    self.__imap.select(self.__mail_folder)
    _, uids = self.__imap.uid('SEARCH', "ALL")
    if not uids[0]:
      return []
    return [int(uid) for uid in uids[0].split()]

  def __get_max_uid(self) -> int:
    """
      Get the highest UID in the mailbox, or -1 if empty.
    """
    try:
      uids = self.__get_uids()
      return max(uids) if len(uids) > 0 else -1
    except Exception:
      logging.critical('Failed to read mailbox during startup.')
      raise

  def __mark_as_unread(self, uid: int):
    """
      Mark mail as unread.
    """
    logging.info(f'Mark mail {uid} as unread.')
    try:
      self.__imap.uid('STORE', str(uid), '-FLAGS', '(\\SEEN)')
    except Exception as e:
      logging.error(f'Error while marking mail {uid} as unread: {e}')
