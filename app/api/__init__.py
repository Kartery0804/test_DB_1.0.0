from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')
print("hello api")

from app.api import sqlsever