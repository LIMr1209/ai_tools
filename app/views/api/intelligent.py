from flask import request, jsonify, current_app
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.helpers.constant import intelligent_category, draw_generate_category

dataInit = {"data": "", "meta": {"message": "", "status_code": 200, }}


@api.expose("/intelligent/category")
class IntelligentCategory(MethodView):
    methods = ["GET"]

    def get(self):
        data = copy.deepcopy(dataInit)
        data['data'] = intelligent_category()
        return jsonify(**data)


@api.expose("/intelligent/handle")
class Intelligent(MethodView):
    methods = ["POST"]

    # decorators = [user_required]

    def post(self):
        data = copy.deepcopy(dataInit)
        myFile = request.files.get("file", None)
        index = force_int(request.values.get('index', 0))
        type = force_int(request.values.get("type", 0))
        if not myFile:
            data["meta"]["message"] = "请上传图片文件"
            data["meta"]["status_code"] = 400
            return data
        if myFile.mimetype not in ["image/jpeg", "image/png", "image/jpg"]:
            data["meta"]["message"] = "上传图片文件的格式有误"
            data["meta"]["status_code"] = 400
            return data
        if type not in list(map(lambda x: x["id"], intelligent_category())):
            data["meta"]["message"] = "请选择正确的设计类型"
            data["meta"]["status_code"] = 400
            return data
        from app.lib.cyclegan.intelligent import intelligent

        res, base64_str = intelligent(image=myFile, index=index, type=type)
        if not res:
            data["meta"]["message"] = base64_str
            data["meta"]["status_code"] = 500
            return data
        else:
            data["data"] = {
                'img': base64_str,
                'index': index,
                'all_index': [0, 1, 2, 3, 4, 5]
            }
        return jsonify(**data)


# 画笔生成
@api.expose("/draw/generate")
class DrawGenerate(MethodView):
    methods = ["POST"]

    # decorators = [user_required]

    def post(self):
        data = copy.deepcopy(dataInit)
        myFile = request.files.get("file", None)
        type = force_int(request.values.get("type", 1))
        img = request.form.get('image_base64', '')
        img = img.replace("data:image/jpeg;base64,", "").replace("data:image/png;base64,", "")
        if not myFile and not img:
            data["meta"]["message"] = "图片参数错误"
            data["meta"]["status_code"] = 400
            return data
        if myFile and myFile.mimetype not in ["image/jpeg", "image/png", "image/jpg"]:
            data["meta"]["message"] = "上传图片文件的格式有误"
            data["meta"]["status_code"] = 400
            return data
        if type not in list(map(lambda x: x["id"], draw_generate_category())):
            data["meta"]["message"] = "请选择正确的生成类型"
            data["meta"]["status_code"] = 400
            return data
        from app.lib.cyclegan.draw_generate import draw_generate
        res, base64_str = draw_generate(base64_data=img, image=myFile, type=type)
        if not res:
            data["meta"]["message"] = base64_str
            data["meta"]["status_code"] = 500
            return data
        else:
            data["data"] = base64_str
        return jsonify(**data)
