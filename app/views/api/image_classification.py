import requests
from flask import request, jsonify, current_app
from app.helpers.file_size import formatSize
from . import api


@api.expose("/image/classification")
def produce_ajx_file():
    """
    图像分类
    Returns:

    """
    methods = ["POST", "GET"]

    def post():
        data = copy.deepcopy(dataInit)
        try:
            f = request.files["file"]
            f_size = formatSize(len(f.read()))
            if f_size > 5:
                data["meta"]["message"] = "传入图片需小于5M"
                data["meta"]["status_code"] = 400
                return jsonify(**data)
            from app.lib.img_recognition.main import recognition
            result = recognition(image=f)
            data['data'] = result
        except Exception as e:
            data["meta"]["message"] = str(e)
            data["meta"]["status_code"] = 500
        return jsonify(**data)

    def get():
        data = copy.deepcopy(dataInit)
        try:
            url = request.args.get("url", "")
            if not url:
                data["meta"]["message"] = "地址不能为空"
                data["meta"]["status_code"] = 400
                return jsonify(**data)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
            try:
                response = requests.get(url, headers=headers, timeout=5)
            except:
                data["meta"]["message"] = "无法解析图片"
                data["meta"]["status_code"] = 400
                return jsonify(**data)
            if response.status_code != 200 and response.status_code != 304:
                data["meta"]["message"] = "无法解析图片"
                data["meta"]["status_code"] = 400
                return jsonify(**data)
            from app.lib.img_recognition.main import recognition
            result = recognition(url=url)
            data['data'] = result
        except Exception as e:
            data["meta"]["message"] = str(e)
            data["meta"]["status_code"] = 500
        return jsonify(**data)

