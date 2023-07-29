from flask_restful import Api
from flask import Flask
import Application.MagicFormula.scheduler
import Application.VolumeBomb.scheduler

app = Flask(__name__)
api = Api(app)

# I love aras and I love you <- by my girlfriend :D