from flask import Blueprint, Response

mod = Blueprint('healthz', __name__)

@mod.route('/healthz')
def index():
    return Response('OK', status=200)
