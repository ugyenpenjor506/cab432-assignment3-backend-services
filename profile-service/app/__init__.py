from flask import Flask

app = Flask(__name__)

from app.controller.ProfileController import ProfileController
