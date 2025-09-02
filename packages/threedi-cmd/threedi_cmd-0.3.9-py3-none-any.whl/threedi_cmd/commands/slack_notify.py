from slack import WebClient
from slack.errors import SlackApiError


class SlackNotifier:
    def __init__(self, token):
        self.client = WebClient(token=token)

    def send_message(self, message: str, channel: str):
        try:
            self.client.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]
            raise e
