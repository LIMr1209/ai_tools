from flask import request, jsonify, current_app
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView

from app.lib.dalle_pytorch.intelligent import intelligent

dataInit = {"data": [], "meta": {"message": "", "status_code": 200, }}

# cmf 生成图片
@api.expose("/cmf/generate")
class CmfGenerate(MethodView):
    methods = ["POST"]

    def post(self):
        data = copy.deepcopy(dataInit)
        type = force_int(request.values.get('type', 1))
        try:
            img = intelligent(request.values.to_dict(), type)
            data["data"].append(img)
        except Exception as e:
            data["meta"]["message"] = str(e)
            data["meta"]["status_code"] = 500
        return jsonify(**data)
