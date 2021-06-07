from flask import request, jsonify
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.lib.stylegan_tensorflow.demo import get_sample as te_sample
from flask import Flask, render_template, request
# pip install gevent-websocket导入IO多路复用模块
from geventwebsocket.websocket import WebSocket  # websocket语法提示

dataInit = {"data": "", "meta": {"message": "", "status_code": 200, }}


@api.route('/websocket')
def websocket():
    client_socket = request.environ.get('wsgi.websocket')  # type:WebSocket
    # print(len(client_list), client_list)


# tensorflow版stylegan
@api.expose("/stylegan_te/generate", methods=["POST"])
class StyleganTeLatent(MethodView):

    def post(self):
        data = copy.deepcopy(dataInit)
        color = request.values.get("color", '')
        img_data_list = te_sample(color=color)
        data["data"] = img_data_list
        return jsonify(**data)

