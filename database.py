import bcrypt
from models import db
from models import User
from models import Food
from models import Food_image
from models import Clothes_image
from models import Clothes_product


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
        user.userid = request[0]
        user.passwd = hashed_password
        user.name = request[2]
        user.phone = request[3]
        user.email = request[4]
        user.address = request[5]
        user.age = request[6]
        user.sex = request[7]
        user.height = request[8]
        user.weight = request[9]
        user.basic_metabolic = basic_metabolic
        user.bmi = bmi
  
        db.session.commit()


    def db_drop_user(self, user):
        db.session.delete(user)
        db.session.commit()


    def get_page_foods(self, page, number):
        start = int(page) * number - number
        end = int(page) * number
        check = Food.query.order_by(Food.id).slice(start, end).all() 

        return check


    def get_page_clothes(self, page, number, sex, season):
        start = int(page) * number - number
        end = int(page) * number
        check = Clothes_product.query.filter_by(sex=sex, season=season).slice(start, end).all() 

        return check


    def insert_foods_image(self, foods, foods_count):
        for i in range(foods_count):
            foods_id = foods[i]['id']
            foods_image = Food_image.query.filter_by(food_id=foods_id).first()
            if foods_image:
                foods[i]['img_src'] = foods_image.img_src

        return foods


    def insert_clothes_image(self, clothes, clothes_count):
        for i in range(clothes_count):
            clothes_id = clothes[i]['id']
            clothes_image = Clothes_image.query.filter_by(product_id=clothes_id).first()
            if clothes_image:
                clothes[i]['img_src'] = clothes_image.img_src

        return clothes