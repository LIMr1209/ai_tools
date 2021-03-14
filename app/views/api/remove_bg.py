import copy
from flask import request, jsonify
from flask.views import MethodView
from . import api
from app.lib.u2net.bg import remove

dataInit = {"data": "", "meta": {"message": "", "status_code": 200, }}
## 图片去底
@api.expose('/image/removebg')
class ImageRemoveBg(MethodView):
    methods = ["POST", "GET"]

    def post(self):
        data = copy.deepcopy(dataInit)
        f = request.files.get("file", None)
        url = request.args.get("url", "")
        if not f or not url:
            data["meta"]["message"] = "请上传图片文件"
            data["meta"]["status_code"] = 400
            return jsonify(**data)
        try:
            if f:
                success, data = remove(image=f)
            else:
                success, data = remove(url=url)
            if success:
                data['data'] = data
            else:
                data["meta"]["message"] = data
                data["meta"]["status_code"] = 500
        except Exception as e:
            data["meta"]["message"] = str(e)
            data["meta"]["status_code"] = 500
        return jsonify(**data)


