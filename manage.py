#!env/bin/python
from app import create_app
from flask_script import Manager, Server, Shell
from geventwebsocket.handler import WebSocketHandler  # 提供WS（websocket）协议处理
from geventwebsocket.server import WSGIServer  # websocket服务承载

app = create_app()
manager = Manager(app)


def _make_context():
    return dict(app=app)


manager.add_command("run", Server(host="127.0.0.1", port=8015))
manager.add_command("shell", Shell(make_context=_make_context))

if __name__ == '__main__':
    app.run()