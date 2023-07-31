from flask_restful import Api
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from Base.Connector import DiscordConnector
from Base.ConfigReader import Config
from datetime import datetime, timedelta
import Application.MagicFormula.scheduler
import Application.VolumeBomb.scheduler

app = Flask(__name__)
api = Api(app)

def stable_check():
    discord = DiscordConnector()
    config = Config()
    message = 'I am alive.'
    discord.sendMessage(config['Discord']['DEV'], message)
sched = BackgroundScheduler(job_defaults={'max_instances': 3})
sched.add_job(stable_check, 'interval', hours=12, next_run_time=datetime.now() + timedelta(seconds=10))
sched.start()

# I love aras and I love you <- by my girlfriend :D