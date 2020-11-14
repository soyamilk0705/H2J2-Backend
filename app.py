import bcrypt
import jwt
from flask import Flask
from flask import render_template
from flask import request, make_response
from flask import jsonify
from flask_cors import CORS
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from models import User
from models import db
from database import DB_Manager
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../H2J2-Front/public', static_folder='../H2J2-Front/public/assets')
DBManager = DB_Manager()
CORS(app)

@app.route('/')
def index():
    return "Hello"


@app.route('/api/check/id', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
)
def check_id(*request_element):
    userid = request_element[0]
    check = User.query.filter_by(userid=userid).first()

    if check is None:
        return {'id': True}
    else:
        return {'id': False}


@app.route('/api/register', methods=['POST'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
    Param('passwd', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]')], required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True),
    Param('address', JSON, str, required=True),
    Param('age', JSON, str, required=True),
    Param('sex', JSON, str, required=True),
    Param('height', JSON, str, required=True),
    Param('weight', JSON, str, required=True),
)
def register(*request_elements):
    userid = request_elements[0]
    phone = request_elements[3]
    email = request_elements[4]

    check_userid = User.query.filter_by(userid=userid).first()
    check_phone = User.query.filter_by(phone=phone).first()
    check_email = User.query.filter_by(email=email).first()

    if (check_userid or check_phone or check_email) is None:
        if request_elements[6] == '남자':
            basic_metabolic = round(66.47 + (13.75 * int(request_elements[9])) + (5 * int(request_elements[8])) - (6.76 * int(request_elements[6])), 1)
        else:
            basic_metabolic = round(655.1 + (9.56 * int(request_elements[9])) + (1.85 * int(request_elements[8])) - (4.68 * int(request_elements[6])), 1)
        
        bmi = round(int(request_elements[9]) / ((int(request_elements[8]) * 0.01) * (int(request_elements[8]) * 0.01)), 1)

        DBManager.db_register(request_elements, basic_metabolic, bmi)
        json_request = {'register': True}

    else:
        json_request = {'register': False}

    return jsonify(json_request)

    
@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
    Param('passwd', JSON, str, required=True)
)
def login(*request_elements):
    userid = request_elements[0]
    passwd = request_elements[1]
    user = User.query.filter_by(userid=userid).first()

    if user is not None:
        is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8'))
        if is_pw_correct:
            payload = {											
                'userid' : userid,
                'exp' : datetime.now() + timedelta(seconds=60 * 60 * 24) # 토큰 만료 시간
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')	
            json_request = {'login': 'True', 'userid': userid, 'level': 1, 'token': token.decode('UTF-8')}
            resp = make_response(json_request)
            resp.headers['Authorization'] = token.decode('UTF-8')
            return resp
        
        else:
            json_request = {'login': False}
    else:
        json_request = {'login': False}

    return jsonify(json_request)


@app.route('/api/logout', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^.{1,50}$')], required=True)
)
def logout(*request_elements):
    if request_elements[0] is not None:
        return {'logout': True}    
    else:
        return {'logout': False}


# @app.route('/api/profile/drop', methods=['POST'])
# @validate_params(
#     Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
#     Param('passwd', JSON, str, required=True)
# )
# def drop_user(*request_elements):
#     token = request.headers.get('Authorization')
#     userid = request_elements[0]
#     passwd = request_elements[1]

#     print("request : ", request_elements[0])
        
#     if token is not None:
#         user = User.query.filter_by(userid=userid).first()
#         if user is not None:
#             is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8')) 
#             if is_pw_correct:
#                 DBManager.db_drop_user(user)
#                 return {'delete': True}

#             return {'delete': False}

#     return {'token': False}




@app.route('/api/profile/edit', methods=['PUT'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
    Param('passwd', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]')], required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True),
    Param('address', JSON, str, required=True),
    Param('age', JSON, str, required=True),
    Param('sex', JSON, str, required=True),
    Param('height', JSON, str, required=True),
    Param('weight', JSON, str, required=True)
)
def edit_profile(*request_elements):
    token = request.headers.get('Authorization')
    userid = request_elements[0]
    
    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            if request_elements[6] == '남자':
                basic_metabolic = round(66.47 + (13.75 * int(request_elements[9])) + (5 * int(request_elements[8])) - (6.76 * int(request_elements[6])), 1)
            else:
                basic_metabolic = round(655.1 + (9.56 * int(request_elements[9])) + (1.85 * int(request_elements[8])) - (4.68 * int(request_elements[6])), 1)
        
            bmi = round(int(request_elements[9]) / ((int(request_elements[8]) * 0.01) * (int(request_elements[8]) * 0.01)), 1)
            
            DBManager.db_edit_profile(request_elements, basic_metabolic, bmi)
    
            return {'edit': True}
        else:
            return {'edit': False}

    return {'token': False}


@app.route('/api/profile/info', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
)
def info_profile(*request_elements):
    token = request.headers.get('Authorization')
    userid = request_elements[0]
    
    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            return jsonify(user.serialize) 

    return {'token': False}


# @app.route('/api/mileage', methods=['GET'])
# @validate_params(
#     Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
# )
# def mileage(*request_elements):
#     token = request.headers.get('Authorization')
#     userid = request_elements[0]
    
#     if token is not None:
#         user = User.query.filter_by(userid=userid).first()
#         if user is not None:
#             return {'mileage': True}

#         return {'mileage': False} 

#     return {'token': False}


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://"  
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.config['SECRET_KEY'] = 'rlawjdtnrlawngusrlagmltndlagywls'
app.config['JWT_SECRET_KEY'] = 'rlawjdtnrlawngusrlagmltndlagywls'

db.init_app(app)
db.app = app
db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

# host='127.0.0.1', port=5000, debug=True
# host='0.0.0.0', port=5000, debug=True
