import dirkules.config as config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import dirkules.TelegramCom

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

# Logging
import logging
from logging.handlers import TimedRotatingFileHandler

log_level = app.config["LOG_LEVEL"]
formatter = logging.Formatter("[%(asctime)s]: %(levelname)s in {%(pathname)s:%(lineno)d} - %(message)s")
handler = TimedRotatingFileHandler("dirkules.log", when="D", interval=1, backupCount=90)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(log_level)

import dirkules.models

# create db if not exists
db.create_all()
# start communication
communicator = TelegramCom.TelegramCom(app)
# start scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# import views
import dirkules.views
