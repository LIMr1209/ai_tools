import copy
from flask import request, jsonify
from flask.views import MethodView
from . import api
from app.lib.u2net.bg import remove

dataInit = {"data": [], "meta": {"message": "", "status_code": 200, }}
## 图片去底
@api.expose('/image/removebg')
class ImageRemoveBg(MethodView):
    methods = ["POST", "GET"]

    def post(self):
        data = copy.deepcopy(dataInit)
        f = request.files.get("file", None)
        base64_data = request.values.get('image_base64','')
        base64_data = base64_data.replace("data:image/jpeg;base64,", "").replace("data:image/png;base64,", "").replace("data:image/jpg;base64,", "")
        if not f:
            data["meta"]["message"] = "请上传图片文件"
            data["meta"]["status_code"] = 400
            return jsonify(**data)
        try:
            success, base_64 = remove(image=f,base64_data=base64_data)
            if success:
                data['data'] = base_64
            else:
                data["meta"]["message"] = data
                data["meta"]["status_code"] = 500
        except Exception as e:
            data["meta"]["message"] = str(e)
            data["meta"]["status_code"] = 500
        return jsonify(**data)

    def get(self):
        data = copy.deepcopy(dataInit)
        url = request.args.get("url", "")
        if not url:
            data["meta"]["message"] = "请传入图片链接"
            data["meta"]["status_code"] = 400
            return jsonify(**data)
        try:
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



