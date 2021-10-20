from flask import request, jsonify
from . import api
from app.helpers.common import force_int
import copy
from flask.views import MethodView
from flask import Flask, render_template, request


dataInit = {"data": "", "meta": {"message": "", "status_code": 200, }}


@api.route('/test/a')
def test_a():
    return 'Test AI'

