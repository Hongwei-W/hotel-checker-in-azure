import requests

PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'

class PushoverHandler:
    def __init__(self, app_token, user_group):
        self.app_token = app_token
        self.user_group = user_group

    def send_message(self, message):
        data = {
            "token": self.app_token,
            "user": self.user_group,
            'message': message["content"],
            'title': message["title"],
        }
        formatted_data = "&".join([f'{key}={value}' for key, value in data.items() if value is not None])
        return requests.post(url=PUSHOVER_URL, data=formatted_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        