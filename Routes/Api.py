from flask_restful import Api
from flask import Flask
import Application.MagicFormula.scheduler

app = Flask(__name__)
api = Api(app)

# I love aras and I love you