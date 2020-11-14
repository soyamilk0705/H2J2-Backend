import bcrypt
from models import User
from models import db


class DB_Manager(object):

    def db_register(self, request, basic_metabolic, bmi):
        hashed_password = bcrypt.hashpw(request[1].encode('utf-8'), bcrypt.gensalt())
        
        user = User(
            userid = request[0],
            passwd = hashed_password,
            name = request[2],
            phone = request[3],
            email = request[4],
            address = request[5],
            age = request[6],
            sex = request[7],
            height = request[8],
            weight = request[9],
            basic_metabolic = basic_metabolic,
            bmi = bmi,
            mileage = 0
        )

        db.session.add(user)
        db.session.commit()


    def db_edit_profile(self, request, basic_metabolic, bmi) :
        hashed_password = bcrypt.hashpw(request[1].encode('utf-8'), bcrypt.gensalt())
        userid = request[0]
        
        user = User.query.filter_by(userid=userid).first()
        user.userid = request[0],
        user.passwd = hashed_password,
        user.name = request[2],
        user.phone = request[3],
        user.email = request[4],
        user.address = request[5],
        user.age = request[6],
        user.sex = request[7],
        user.height = request[8],
        user.weight = request[9],
        user.basic_metabolic = basic_metabolic,
        user.bmi = bmi,
        user.mileage = mileage
  
        db.session.commit()


    def db_drop_user(self, user):

        db.session.delete(user)
        db.session.commit()