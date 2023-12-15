# cython: language_level=3
import functools
import os

from flask import (
    current_app,
    g,
    flash,
    request,
    url_for,
    jsonify,
    redirect,
    Blueprint,
    app,
    abort,
)


# 登陆验证
def user_required(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        if not g.user:
            abort(401)
        return f(*args, **kwargs)

    return decorator


# 判断ajax 请求
def request_wants_json():
    """Based on `Armin's snippet <http://flask.pocoo.org/snippets/45/>`.
        """
    return request.environ.get("HTTP_X_REQUESTED_WITH", "").lower() == "xmlhttprequest"


#  app 注册 蓝图 和 method_view
def register_api(app, routers):
    """
    注册蓝图和自定义MethodView
    """
    for router in routers:
        if isinstance(router, Blueprint):
            app.register_blueprint(router)
        else:
            try:
                endpoint = router.__name__
                view_func = router.as_view(endpoint)
                url = "/{}/".format(router.__name__.lower())
                if "GET" in router.__methods__:
                    app.add_url_rule(
                        url,
                        defaults={"key": None},
                        view_func=view_func,
                        methods=["GET",],
                    )
                    app.add_url_rule(
                        "{}<string:key>".format(url),
                        view_func=view_func,
                        methods=["GET",],
                    )
                if "POST" in router.__methods__:
                    app.add_url_rule(url, view_func=view_func, methods=["POST",])
                if "PUT" in router.__methods__:
                    app.add_url_rule(
                        "{}<string:key>".format(url),
                        view_func=view_func,
                        methods=["PUT",],
                    )
                if "DELETE" in router.__methods__:
                    app.add_url_rule(
                        "{}<string:key>".format(url),
                        view_func=view_func,
                        methods=["DELETE",],
                    )
            except Exception as e:
                raise ValueError(e)


# 蓝图 添加url  装饰器
class SeniorBlueprint(Blueprint):
    def expose(self, rule, **options):
        def decorator(v):
            endpoint = options.pop("endpoint", v.__name__)
            options["view_func"] = v.as_view(endpoint)
            options["methods"] = v.methods
            self.add_url_rule(rule, **options)
            return v

        return decorator


# 缓存带动态参数的视图函数
def make_cache_key(*args, **kwargs):
    """Dynamic creation the request url."""
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args


# 表态资源url
def static_url(url):
    domain = current_app.config["STATIC_URL"]
    return os.path.join(domain, url).replace("\\", "/")
