# cython: language_level=3
# coding: utf-8
from app.helpers.interceptor import SeniorBlueprint

api = SeniorBlueprint("api", __name__, url_prefix="/api")
from . import remove_bg
