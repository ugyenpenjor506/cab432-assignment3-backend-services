from flask import Flask
from app.helper.SecretManager import get_secrets


app = Flask(__name__)


from app.controller.FeedbackController import FeedbackContoller
