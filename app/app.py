from flask import Flask
from flask_socketio import SocketIO

from .config import Config

socketio = SocketIO()

app = Flask(__name__)

def create_app(event):
    print("Starting flask application")
    event.config.from_object(Config)

    socketio.init_app(event)

    from . import routes
    event.register_blueprint(routes.bp)

    from . import events

    return events


runner = create_app(app)

if __name__ == '__main__':
    socketio.run(runner, debug=True)
