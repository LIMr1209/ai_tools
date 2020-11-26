from flask import request, jsonify, current_app
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.helpers.constant import intelligent_category

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

        res, base64_str_list = intelligent(image=myFile, index=index, type=type)
        if not res:
            data["meta"]["message"] = base64_str_list
            data["meta"]["status_code"] = 500
            return data
        else:
            data["data"] = {
                'img': base64_str_list,
                'index': index,
                'all_index': [0, 1, 2, 3, 4, 5]
            }
        return jsonify(**data)


@api.expose("/test")
class Test(MethodView):
    methods = ["GET"]

    def get(self):
        current_app.logger.warning('测试')
        current_app.logger.error('测试')
        current_app.logger.debug('测试')
        current_app.logger.critical('测试')
        current_app.logger.info('测试')


        return jsonify(success=True)
