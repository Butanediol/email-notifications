import requests

class TgSender:
  
  __sendMessageUrl = 'https://api.telegram.org/bot<token>/sendMessage'

  def __init__(self, token, chatId):
    if not token or not chatId:
      raise Exception('Each parameter must not be empty') 
    self.__tgApiToken = token
    self.__sendMessageUrl = self.__sendMessageUrl.replace('<token>', token)
    self.__chatId = chatId
    
  def send(self, text):
    data = {'chat_id': self.__chatId, 'text': text}
    try:
      requests.post(self.__sendMessageUrl, data=data)
    except:
      print('Failed to send notification. Check the availability of Telegram servers (for example, Telegram website) from place where the script is running')