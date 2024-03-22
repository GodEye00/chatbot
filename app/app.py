
import eventlet
eventlet.monkey_patch()

from flask import Flask
from celery import Celery
import redis
from flask_socketio import SocketIO
from flask_cors import CORS
# from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os


from .config import Config

LOG_FILE = 'app.log'


app = Flask(__name__)
celery = Celery(__name__, include=['app.services.tasks'])
socketio = SocketIO(app, message_queue=os.environ.get('CACHE_REDIS_URL'), cors_allowed_origins="*")


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
    
    CORS(app)
    # CSRFProtect(app)

    redis_url = event.config['CACHE_REDIS_URL']
    r = redis.Redis.from_url(redis_url)
    app.redis = r

    socketio.init_app(event)
    make_celery(event)

    from . import routes
    event.register_blueprint(routes.bp)

    from . import events

    return events


def make_celery(app):
    """
    Configure the Celery application to work within the Flask application context.
    """
    # Directly load configurations from the Flask app to Celery
    celery.config_from_object(app.config, namespace='CELERY')
    celery.conf.broker_connection_retry_on_startup = True
    celery.conf.result_expires = 3600 # Tasks delete after 1hr
    # celery.conf.update({
    #     'worker_pool': 'eventlet'
    # })
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery

runner = create_app(app)

if __name__ == '__main__':
    socketio.run(runner, debug=True)
