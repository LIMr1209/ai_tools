from flask import request, jsonify, current_app
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from app.helpers.common import pil_to_base64
from app.helpers.constant import intelligent_category, draw_generate_category

dataInit = {"data": [], "meta": {"message": "", "status_code": 200, }}


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


# 上传 转base64
@api.expose('/draw/upload')
class DrawUpload(MethodView):
    methods = ["POST"]

    def post(self):
        data = copy.deepcopy(dataInit)
        myFile = request.files.get("file", None)
        if myFile and myFile.mimetype not in ["image/jpeg", "image/png", "image/jpg"]:
            data["meta"]["message"] = "上传图片文件的格式有误"
            data["meta"]["status_code"] = 400
            return data
        data["data"] = {
            'img': pil_to_base64(myFile),
        }
        return jsonify(**data)


# 画笔或者上传生成
@api.expose("/draw/generate")
class DrawGenerate(MethodView):
    methods = ["POST"]

    # decorators = [user_required]

    def post(self):
        data = copy.deepcopy(dataInit)
        myFile = request.files.get("file", None)
        type = force_int(request.values.get("type", 1))
        index = force_int(request.values.get('index', 0))
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
        res, base64_str = draw_generate(base64_data=img, image=myFile, index=index, type=type)
        if not res:
            data["meta"]["message"] = base64_str
            data["meta"]["status_code"] = 500
            return data
        else:
            data["data"] = {
                'img': base64_str,
                'index': index,
                'all_index': [0, 1, 2, 3]
            }
        return jsonify(**data)


# 图片融合发散
@api.expose("/fuse/divergence")
class FuseDivergence(MethodView):
    methods = ["POST"]

    # decorators = [user_required]

    def post(self):
        data = copy.deepcopy(dataInit)
        type = force_int(request.values.get("type", 1))
        img_1 = request.values.get('image_1_base64', '')
        img_2 = request.values.get('image_2_base64', '')
        img_1 = img_1.replace("data:image/jpeg;base64,", "").replace("data:image/png;base64,", "")
        img_2 = img_2.replace("data:image/jpeg;base64,", "").replace("data:image/png;base64,", "")
        file_name1 = request.values.get('file_name1', '')
        file_name2 = request.values.get('file_name2', '')
        if not img_1 and not img_2:
            data["meta"]["message"] = "图片参数错误"
            data["meta"]["status_code"] = 400
            return data
        if not file_name1.endswith('_origin.jpg') or not file_name2.endswith('_origin.jpg'):
            if type == 2:
                try:
                    from app.lib.stylegan_pytorch.projector import run_projection
                    image_base64_1, image_base64_2, image_base64_3, image_base64_4 = run_projection(img_1, img_2, type)
                    data["data"] = [image_base64_1, image_base64_2, image_base64_3, image_base64_4]
                except Exception as e:
                    data["meta"]["message"] = str(e)
                    data["meta"]["status_code"] = 500
        else:
            type = file_name1.split('_')[0]
            group = file_name1.split('_')[1]
            try:
                for i in range(1, 5):
                    img = pil_to_base64('static/image/result/{}/{}_{}_result.jpg'.format(type, group, i))
                    data["data"].append(img)
            except:
                data["data"] = []
        return jsonify(**data)