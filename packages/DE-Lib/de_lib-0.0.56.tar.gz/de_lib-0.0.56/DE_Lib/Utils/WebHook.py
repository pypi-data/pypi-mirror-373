import requests
import json

class WEBHOOK:
    def __init__(self):
        ...

    @staticmethod
    def post_message_to_slack(token, channel, text, icon_emoji, username, blocks=None,
                              url="https://slack.com/api/chat.postMessage"):
        return requests.post(url,
                             {'token': token,
                              'channel': channel,
                              'text': text,
                              'icon_emoji': icon_emoji,
                              'username': username,
                              'blocks': json.dumps(blocks) if blocks else None
                              }
                             ).json()
