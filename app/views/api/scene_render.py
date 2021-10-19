from flask import request, jsonify, current_app
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.helpers.common import pil_to_base64

metaInit = {"data": [], "meta": {"message": "", "status_code": 200, }}




@api.route('/scene/list', methods=["GET"])
def scene_render_scene_list():
    meta = copy.deepcopy(metaInit)
    data = [
        {'id': 1, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614da03ae0e96e5a77e1c649-0-p750x422.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/BG1.glb'}, 
        {'id': 2, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614da03ae0e96e5a77e1c649-1-p750x422.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/BG2.glb'}, 
        {'id': 3, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614da03ae0e96e5a77e1c649-2-p750x422.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/BG3.glb'}, 
             
    ]
    meta['data'] = data

    return jsonify(**meta)


@api.route('/product/list', methods=["GET"])
def scene_render_product_list():
    meta = copy.deepcopy(metaInit)
    data = [
        {'id': 1, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614d9f8538f58b85cbe44ca3-0-avb.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/Product1.glb'}, 
        {'id': 2, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614d9fed4b7865954de1883d-0-avb.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/Product2.glb'}, 
        {'id': 3, 'cover_url': 'https://p4.taihuoniao.com/photo/20210924/614d9fed4b7865954de1883d-1-avb.jpg', 'mode_url': 'https://s3.taihuoniao.com/3d_model/Product3.glb'}, 
             
    ]
    meta['data'] = data

    return jsonify(**meta)


@api.route('/render/show', methods=["GET"])
def scene_render_show():
    meta = copy.deepcopy(metaInit)
    scene_id = force_int(request.values.get('scene_id', 0))
    product_id = force_int(request.values.get('product_id', 0))
    if not scene_id or not product_id:
        meta["meta"]["message"] = "缺少请求参数！"
        meta["meta"]["status_code"] = 400
        return jsonify(**meta)

    data = [
             
    ]
    meta['data'] = data

    return jsonify(**meta)



@api.expose("/scene/test")
class SceneIndex(MethodView):
    methods = ["POST"]
    pass
