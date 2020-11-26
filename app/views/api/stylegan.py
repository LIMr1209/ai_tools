import random

from flask import request, jsonify
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.lib.stylegan.demo import get_sample as py_sample
from app.lib.stylegan_tensorflow.demo import get_sample as te_sample
from flask import Flask, render_template, request
# pip install gevent-websocket导入IO多路复用模块
from geventwebsocket.websocket import WebSocket  # websocket语法提示

from ...helpers.color_cluster_1126 import majoColor_inrange

dataInit = {"data": "", "meta": {"message": "", "status_code": 200, }}


@api.route('/websocket')
def websocket():
    client_socket = request.environ.get('wsgi.websocket')  # type:WebSocket
    # print(len(client_list), client_list)


@api.expose("/stylegan/generate", methods=["POST"])
class StyleganGenerate(MethodView):

    def post(self):
        data = copy.deepcopy(dataInit)
        seed = request.values.get('seed', 0)
        img_data, seed = py_sample('g', seed)
        data["data"] = {
            'img': img_data,
            'seed': seed,
        }
        return jsonify(**data)


@api.expose("/stylegan_te/generate", methods=["POST"])
class StyleganTeLatent(MethodView):

    def post(self):
        data = copy.deepcopy(dataInit)
        seed = force_int(request.values.get("seed", 0))
        color = request.values.get("color", '')
        if color:
            seed_list = [random.randint(1, 100000) for i in range(50)]
            img_data_list = []
            for i in seed_list:
                img_data, seed, image_cv2 = te_sample(i)
                color_tags = majoColor_inrange(image_cv2)
                if color_tags == color:
                    img_data_list.append({
                        'img': img_data,
                        'seed': seed,
                    })
            data["data"] = img_data_list
        else:
            img_data, seed = te_sample(seed)
            data["data"] = [{
                'img': img_data,
                'seed': seed,
            }]

        return jsonify(**data)


@api.expose("/stylegan/latent", methods=["POST"])
class StyleganLatent(MethodView):

    def post(self):
        data = copy.deepcopy(dataInit)
        i = force_int(request.values.get("i", 0))
        d = force_int(request.values.get('d', 0))
        seed = force_int(request.values.get("seed", 0))

        img_data, seed = py_sample("l", seed, i=i, d=d)
        data["data"] = {
            'img': img_data,
            'seed': seed,
        }
        return jsonify(**data)
