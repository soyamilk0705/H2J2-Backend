import bcrypt
import jwt
from flask import Flask
from flask import render_template
from flask import request, make_response
from flask import jsonify
from flask_cors import CORS
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from models import db
from models import User
from models import Food
from models import Food_image
from models import Clothes_product
from models import Clothes_image
from database import DB_Manager
from datetime import datetime, timedelta

app = Flask(__name__)
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


@app.route('/api/profile/drop', methods=['POST'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  # 소문자와 숫자만 가능
    Param('passwd', JSON, str, required=True)
)
def drop_user(*request_elements):
    token = request.headers.get('Authorization')
    userid = request_elements[0]
    passwd = request_elements[1]
        
    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8')) 
            if is_pw_correct:
                DBManager.db_drop_user(user)
                return {'delete': True}

            return {'delete': False}

    return {'token': False}


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
    Param('weight', JSON, str, required=True),
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
    Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True), 
)
def info_profile(*request_elements):
    token = request.headers.get('Authorization')
    userid = request_elements[0]
    
    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            return jsonify(user.serialize) 

    return {'token': False}


@app.route('/api/mileage', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
)
def mileage(*request_elements):
    token = request.headers.get('Authorization')
    userid = request_elements[0]

    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            return {'mileage': user.mileage}

    return {'token': False}


@app.route('/api/food/list', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def list_food(*request_elements):
    page = request_elements[0]
    check = DBManager.get_page_foods(page, 5)

    if not check:
        return {'list': 'False'}

    else:
        foods = [t.serialize for t in check]
        page_count = Food.query.count()
        foods = DBManager.insert_foods_image(foods)
        
        if (page_count % 5) == 0:
            page = int(page_count / 5)
        else:
            page = int((page_count / 5) + 1)
    
        food_list = {'foods': foods}, {'page': page}   

    return jsonify(food_list)



@app.route('/api/fassion/women/ss', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def women_ss(*request_elements):
    page = request_elements[0]
    check = DBManager.get_page_clothes(page, 50, '여', '2020S/S')

    if not check:
        return {'list': 'False'}

    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='여', season='2020S/S').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 50) == 0:
            page = int(page_count / 50)
        else:
            page = int((page_count / 50) + 1)
    
        clothes_list = {'clothes': clothes}, {'page': page}   

    return jsonify(clothes_list)



@app.route('/api/fassion/women/fw', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def women_fw(*request_elements):
    page = request_elements[0]
    check = DBManager.get_page_clothes(page, 50, '여', '2020F/W')

    if not check:
        return {'list': 'False'}

    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='여', season='2020F/W').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 50) == 0:
            page = int(page_count / 50)
        else:
            page = int((page_count / 50) + 1)
    
        clothes_list = {'clothes': clothes}, {'page': page}   

    return jsonify(clothes_list)



@app.route('/api/fassion/men/ss', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def men_ss(*request_elements):
    page = request_elements[0]
    check = DBManager.get_page_clothes(page, 50, '남', '2020S/S')

    if not check:
        return {'list': 'False'}

    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='남', season='2020S/S').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 50) == 0:
            page = int(page_count / 50)
        else:
            page = int((page_count / 50) + 1)
    
        clothes_list = {'clothes': clothes}, {'page': page}   

    return jsonify(clothes_list)



@app.route('/api/fassion/men/fw', methods=['GET'])
@validate_params(
    Param('page', GET, str, rules=[Pattern(r'\d')], required=True)
)
def men_fw(*request_elements):
    page = request_elements[0]
    check = DBManager.get_page_clothes(page, 50, '남', '2020F/W')

    if not check:
        return {'list': 'False'}

    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='남', season='2020F/W').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 50) == 0:
            page = int(page_count / 50)
        else:
            page = int((page_count / 50) + 1)
    
        clothes_list = {'clothes': clothes}, {'page': page}   

    return jsonify(clothes_list)


@app.route('/api/exercise/arm', methods=['GET'])
def ex_arm():
    check = DBManager.get_exercise('arm')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/shoulder', methods=['GET'])
def ex_shoulder():
    check = DBManager.get_exercise('shoulder')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/lower_body', methods=['GET'])
def ex_lower_body():
    check = DBManager.get_exercise('lower_body')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/chest', methods=['GET'])
def ex_chest():
    check = DBManager.get_exercise('chest')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/back', methods=['GET'])
def ex_back():
    check = DBManager.get_exercise('back')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/whole_body', methods=['GET'])
def ex_whole_body():
    check = DBManager.get_exercise('whole_body')

    print(check)
    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/belly', methods=['GET'])
def ex_belly():
    check = DBManager.get_exercise('belly')

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/arm/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_arm(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('arm')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/shoulder/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_shoulder(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('shoulder')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/lower_body/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_lower_body(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('lower_body')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/chest/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_chest(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('chest')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/back/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_back(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('back')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/whole_body/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_whole_body(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('whole_body')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/belly/search', methods=['GET'])
@validate_params(
    Param('title', GET, str, rules=[Pattern(r'^.{1,30}$')], required=True)
)
def search_belly(*request_elements):
    kw = request_elements[0]
    exercises = DBManager.get_exercise('belly')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list': 'False'}

    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)



app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:rootpassword@localhost:3306/h2j2_project"  
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
