import requests
import json

class BarkSender:

  def __init__(self, token: str, baseUrl: str):
    if not token:
      raise Exception('Each parameter must not be empty') 
    self.__deviceToken = token
    self.__sendMessageUrl = baseUrl + '/' + token
    
  def send(self, title: str, content: str, icon: str = '', url: str = ''):
    try:
      response = requests.post(
        url=self.__sendMessageUrl,
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "body": content,
            "group": "Email",
            "title": title,
            "icon": url,
            "url": url
        }),
        )
      print('Response HTTP Status Code: {status_code}'.format(
          status_code=response.status_code))
      print('Response HTTP Response Body: {content}'.format(
          content=response.content))
    except requests.exceptions.RequestException:
      print('HTTP Request failed')