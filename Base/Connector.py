from pymongo import MongoClient
from discord import Webhook, RequestsWebhookAdapter
from Base.ConfigReader import Config
from Base.Wrapper import singleton


class Connector(object):
    def __init__(self):
        self.config = Config()

@singleton
class MongoDBConnector(Connector):
    def __init__(self):
        super().__init__()
        config = self.config["MongoDB"]
        host = config["host"]
        self._mongoConnection = MongoClient(host=host)

    def getConn(self):
        return self._mongoConnection


class DiscordConnector:
    def sendMessage(self, webhook, message):
        webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
        webhook.send(message)