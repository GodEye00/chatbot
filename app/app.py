from flask import Flask
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler
import os

from .config import Config

socketio = SocketIO()

app = Flask(__name__)

LOG_FILE = 'app.log'

def create_app(event):
    # Create a rotating file handler which logs even debug messages
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(os.path.join('logs', LOG_FILE), maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    event.logger.addHandler(file_handler)
    event.logger.setLevel(logging.INFO)
    event.logger.info('Flask application startup')
    event.config.from_object(Config)

    socketio.init_app(event)

    from . import routes
    event.register_blueprint(routes.bp)

    from . import events

    return events


runner = create_app(app)

if __name__ == '__main__':
    socketio.run(runner, debug=True)
