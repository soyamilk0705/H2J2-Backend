import bcrypt
import jwt
from flask import Flask, request, jsonify, make_response
from flask_request_validator import Param, JSON, GET, Pattern, validate_params
from flask_cors import CORS
from models import User, db, Food, Food_image, Clothes_product, Clothes_image, Exercise
from database import DB_Manager
from datetime import datetime, timedelta

app = Flask(__name__)
DBManager = DB_Manager()
CORS(app)   # 모든 출처에서의 오청을 허용

@app.route('/')
def index():
    return "Hello"

@app.route('/api/check/id', methods=['GET'])
def check_id():    
    userid = request.args.get('userid')
    check = User.query.filter_by(userid=userid).first() 

    if check is None:
        return {'id': True}
    else:
        return {'id': False}
    

# @app.route('/api/check/id', methods=['GET'])
# def check_id():
#     print(request.args.get('userid'))
#     return {'id': True}


@app.route('/api/register', methods=['POST'])
def register():
    # json은 딕셔너리와 리스트로 구성된 데이터 구조를 가지고 있으며 튜플로 파싱하는건 데이터를 사용하기가 더 어렵고 복잡해질 수 있음
    # request.get_json()은 해당 요청에서 JSON 형식으로 전달된 데이터를 파싱하여 Python의 딕셔너리나 리스트 형태로 반환해줌.

    request_data = request.get_json()

    userid = request_data['userid']
    phone = request_data['phone']
    email = request_data['email']

    check_userid = User.query.filter_by(userid=userid).first()
    check_phone = User.query.filter_by(phone=phone).first()
    check_email = User.query.filter_by(email=email).first()

    if (check_userid or check_phone or check_email) is None:
        if request_data['sex'] == '남자':
            basic_metabolic = round(66.47 + (13.75 * int(request_data['weight'])) + (5 * int(request_data['height'])) - (6.76 * int(request_data['age'])), 1)
        else:
            basic_metabolic = round(655.1 + (9.56 * int(request_data['weight'])) + (1.85 * int(request_data['height'])) - (4.68 * int(request_data['age'])), 1)
    
        bmi = round(int(request_data['weight']) / ((int(request_data['height']) * 0.01) * (int(request_data['height']) * 0.01)), 1)

        DBManager.db_register(request_data, basic_metabolic, bmi)
        json_request = {'register': True}
    
    else:
        json_request = {'register': False}

    return jsonify(json_request)
    

@app.route('/api/login', methods=['POST'])
def login():
    request_data = request.get_json()

    userid = request_data['userid']
    passwd = request_data['passwd']

    user = User.query.filter_by(userid=userid).first()

    if user is not None:
        is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8'))
        if is_pw_correct:
            # payload: 로그인 후 발급할 JWT 토큰의 내용을 정의(여기서는 사용자 아이디와 토큰 만료 시간(exp)을 포함하고 있음)
            payload = {
                'userid' : userid,
                'exp' : datetime.now() + timedelta(seconds=60 * 60 * 24)
            }
            
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')      # JWT 토큰을 생성 payload를 토대로 토큰을 생성하며, 시크릿 키 (JWT_SECRET_KEY)를 사용하여 서명
            json_request = {'login' : 'True', 'userid' : userid, 'level' : 1, 'token' : token}
            resp = make_response(json_request)      # 응답에 추가적인 설정이나 헤더, 쿠키 등을 포함하고 싶은 경우 make_response() 함수를 사용하여 응답 객체를 생성하고 그에 필요한 설정을 추가할 수 있음
            resp.headers['Authorization'] = token     # 응답 헤더에 JWT 토큰을 추가(클라이언트가 서버로부터 토큰을 받을 수 있음)
            return resp
        else:
            json_request = {'login' : False}
    else:
        json_request = {'login' : False}

    return jsonify(json_request)


@app.route('/api/logout', methods=['GET'])
def logout(userid):
    if userid is not None:
        return {'logout': True}
    else:
        return {'logout': False}


@app.route('/api/profile/drop', methods=['GET'])
def drop_user():
    request_data = request.get_json()
    token = request.headers.get('Authorization')
    userid = request_data['userid']
    passwd = request_data['passwd']

    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8'))
            if is_pw_correct:
                DBManager.db_drop_user(user)
                return {'delete': True}
            return {'delete': False}
    
    return {'token': False}

@app.route('/api/profile/info', methods=['GET'])
def info_profile():
    token = request.headers.get('Authorization')
    userid = request.args.get('userid')

    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            return jsonify(user.serialize)

    return {'token': False}


@app.route('/api/profile/edit', methods=['PUT'])
def edit_profile():
    request_data = request.get_json()
    token = request.headers.get('Authorization')
    userid = request_data['userid']

    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            if request_data['sex'] == '남자':
                basic_metabolic = round(66.47 + (13.75 * int(request_data['weight'])) + (5 * int(request_elements['height'])) - (6.76 * int(request_elements['age'])), 1)
            else:
                basic_metabolic = round(655.1 + (9.56 * int(request_data['weight'])) + (1.85 * int(request_elements['height'])) - (4.68 * int(request_elements['age'])), 1)
            
            bmi = round(int(request_data['weight']) / ((int(request_data['height']) * 0.01) * (int(request_elements['height']) * 0.01)), 1)
            DBManager.db_edit_profile(request_data, basic_metabolic, bmi)

            return {'edit': True}
        else:
            {'edit': False}    

    return {'token': False}


@app.route('/api/mileage', methods=['GET'])
def mileage():
    request_data = request.get_json()
    token = request.header.get('Authorization')
    userid = request_data['userid']

    if token is not None:
        user = User.query.filter_by(userid=userid).first()
        if user is not None:
            return {'mileage': user.mileage}

    return {'token': False}


@app.route('/api/food/list', methods=['GET'])
def list_food():
    page = request.args.get('page')
    check = DBManager.get_page_foods(page, 5)

    if not check:
        return {'list': False}

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


@app.route('/api/fassion/men/fw', methods=['GET'])
def fassion_man_fw():
    page = request.args.get('page')
    check = DBManager.get_page_clothes(page, 40, '남자', '2020F/W')

    if not check:
        return {'list': False}
    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='남자', season='2020F/W').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 40) == 0:
            page = int(page_count / 40)
        else:
            page = int((page_count / 40) + 1)

        clothes_list = {'clothes': clothes}, {'page': page}

    return jsonify(clothes_list)


@app.route('/api/fassion/men/ss', methods=['GET'])
def fassion_man_ss():
    page = request.args.get('page')
    check = DBManager.get_page_clothes(page, 40, '남자', '2020S/S')

    if not check:
        return {'list': False}
    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='남자', season='2020S/S').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 40) == 0:
            page = int(page_count / 40)
        else:
            page = int((page_count / 40) + 1)
        
        clothes_list = {'clothes': clothes} , {'page': page}
        
    return jsonify(clothes_list)


@app.route('/api/fassion/women/fw', methods=['GET'])
def fassion_woman_fw():
    page = request.args.get('page')
    check = DBManager.get_page_clothes(page, 40, '여자', '2020F/W')

    if not check:
        return {'list': False}
    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='여자', season='2020F/W').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 40) == 0:
            page = int(page_count / 40)
        else:
            page = int((page_count / 40) + 1)
        
        clothes_list = {'clothes': clothes} , {'page': page}
        
    return jsonify(clothes_list)
        

@app.route('/api/fassion/women/ss', methods=['GET'])
def fassion_woman_ss():
    page = request.args.get('page')
    check = DBManager.get_page_clothes(page, 40, '여자', '2020S/S')

    if not check:
        return {'list': False}
    else:
        clothes = [t.serialize for t in check]
        page_count = Clothes_product.query.filter_by(sex='여자', season='2020S/S').count()
        clothes = DBManager.insert_clothes_image(clothes)

        if (page_count % 40) == 0:
            page = int(page_count / 40)
        else:
            page = int((page_count / 40) + 1)
        
        clothes_list = {'clothes': clothes} , {'page': page}
        
    return jsonify(clothes_list)
        
# clothes는 한 페이지에 40개의 아이템들이 들어가서 for문으로 serialize 하고
# exercise는 한 페이지에 1개의 아이템만 들어가서 1개만 serialize 함
@app.route('/api/exercise/arm', methods=['GET'])
def exercise_arm():
    page = request.args.get('page')
    check = DBManager.get_exercise('arm')

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercises_list = {'exercises': exercises}, {'page':page_count}

    return jsonify(exercises_list)

@app.route('/api/exercise/shoulder', methods=['GET'])
def exercise_shoulder():
    page = request.args.get('page')
    check = DBManager.get_exercise('shoulder')

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercises_list = {'exercises': exercises}, {'page': page_count}

    return jsonify(exercises_list)

@app.route('/api/exercise/lower_body', methods=['GET'])
def exercise_lower_body():
    page = request.args.get('page')     # TODO: page 어떻게 들어오는지 확인
    check = DBManager.get_exercise('lower_body')

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)
        
        exercise_list = {'exercises': exercises}, {'page': page_count}

    return jsonify(exercise_list)


@app.route('/api/exercise/chest', methods=['GET'])
def exercise_chest():
    page = request.args.get('page')
    check = DBManager.get_exercise('chest')    

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1 
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercise_list = {'exercises': exercises}, {'page': page}

    return jsonify(exercise_list)


@app.route('/api/exercise/whole_body', methods=['GET'])
def exercise_whole_body():
    page = request.args.get('page')
    check = DBManager.get_exercise('whole_body')    

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1 
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercise_list = {'exercises': exercises}, {'page': page}

    return jsonify(exercise_list)


@app.route('/api/exercise/belly', methods=['GET'])
def exercise_belly():
    page = request.args.get('page')
    check = DBManager.get_exercise('belly')    

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1 
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercise_list = {'exercises': exercises}, {'page': page}

    return jsonify(exercise_list)


@app.route('/api/exercise/back', methods=['GET'])
def exercise_back():
    page = request.args.get('page')
    check = DBManager.get_exercise('back')    

    if not check:
        return {'list': False}
    else:
        ex_page = int(page) - 1 
        page_count = int(len(check))
        exercises = [check[ex_page].serialize]
        exercises = DBManager.insert_ex_video(exercises)

        exercise_list = {'exercises': exercises}, {'page': page}

    return jsonify(exercise_list)
    

@app.route('/api/exercise/arm/search', methods=['GET'])
def exercise_arm_search():
    kw = request.args.get('title')

    exercises = DBManager.get_exercise('arm')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list', False}
    else:
        exercises = [t.serialize for t in check]    # list -> dictionary
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)


@app.route('/api/exercise/shoulder/search', methods=['GET'])
def exercise_shoulder_search():
    kw = request.args.get('title')

    exercises = DBManager.get_exercise('shoulder')
    check = DBManager.search_exercise(exercises, kw)

    if not check:
        return {'list', False}
    else:
        exercises = [t.serialize for t in check]
        exercises = DBManager.insert_ex_video(exercises)

    return jsonify(exercises)



app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False           # 모델 수정 추적(모델 수정에 대한 변경사항 추적여부 -> 리소스 절약, 성능개선)
db.init_app(app)        # SQLAlchemy 인스턴스를 Flask 앱과 연결하는 역할
db.app = app            # SQLAlchemy 인스턴스의 app 속성을 직접 설정하는 방법입니다. 이렇게 설정해야 SQLAlchemy가 어떤 Flask 앱과 연결되어 있는지 알 수 있습니다. 일반적으로 db.init_app(app)을 사용하여 연결하지만, 때로는 직접 설정할 필요가 있을 수 있습니다.
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)

