from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.String(100), primary_key=True, nullable=False)
    passwd = db.Column(db.String(100))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(300), unique=True)
    address = db.Column(db.String(300))
    age = db.Column(db.String(30))
    sex = db.Column(db.String(30))
    height = db.Column(db.String(30))
    weight = db.Column(db.String(30))
    basic_metabolic = db.Column(db.String(30))
    bmi = db.Column(db.String(30))
    mileage = db.Column(db.String(30))

    @property
    def serialize(self):
        return{
            'userid': self.userid,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'age': self.age,
            'sex': self.sex,
            'height': self.height,
            'weight': self.weight,
            'basic_metabolic': self.basic_metabolic,
            'bmi': self.bmi
        }


class Clothes_site(db.Model):
    __tablename__ = 'clothes_site'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(30))
    url = db.Column(db.String(300), unique=True)
    setting = db.Column(db.String(30))
    site = db.relationship('Clothes_category', backref='clothes_site', lazy=True)


class Clothes_category(db.Model):
    __tablename__ = 'clothes_category'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    site_id = db.Column(db.ForeignKey('clothes_site.id'), nullable=False)
    name = db.Column(db.String(300))
    url = db.Column(db.String(300), unique=True)
    category = db.relationship('Clothes_product', backref='clothes_category', lazy=True)


class Clothes_product(db.Model):
    __tablename__ = 'clothes_product'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category_id = db.Column(db.ForeignKey('clothes_category.id'), nullable=False)
    brand = db.Column(db.String(30))
    name = db.Column(db.String(300))
    price = db.Column(db.String(30))
    season = db.Column(db.String(30))
    sex = db.Column(db.String(30))
    url = db.Column(db.String(300), unique=True)
    fin = db.Column(db.String(30))
    product = db.relationship('Clothes_image', backref='clothes_product', lazy=True)


class Clothes_image(db.Model):
    __tablename__ = 'clothes_image'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.ForeignKey('clothes_product.id'), nullable=False)
    img_src = db.Column(db.String(300), unique=True)
    file_path = db.Column(db.String(300))
    file_name = db.Column(db.String(30))
    extension = db.Column(db.String(30))


class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(300), unique=True)
    exercise_type = db.Column(db.String(30))
    ex_video = db.relationship('Exercise_video', backref='exercise', lazy=True)
    ex_area = db.relationship('Exercise_area', backref='exercise', lazy=True)


class Exercise_video(db.Model):
    __tablename__ = 'ex_video'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ex_id = db.Column(db.ForeignKey('exercise.id'), nullable=False)
    url = db.Column(db.String(300), unique=True)


class Exercise_area(db.Model):
    __tablename__ = 'ex_area'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ex_id = db.Column(db.ForeignKey('exercise.id'), nullable=False)
    arm = db.Column(db.String(30))
    shoulder = db.Column(db.String(30))
    lower_body = db.Column(db.String(30))
    chest = db.Column(db.String(30))
    back = db.Column(db.String(30))
    whole_body = db.Column(db.String(30))
    belly = db.Column(db.String(30))


class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(300), unique=True)
    carbohydrate = db.Column(db.String(30))
    protein = db.Column(db.String(30))
    fat = db.Column(db.String(30))
    calorie = db.Column(db.String(30))
    url = db.Column(db.String(300), unique=True)
    food_image = db.relationship('Food_image', backref='food', lazy=True)

    @property
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'carbohydrate': self.carbohydrate,
            'protein': self.protein,
            'fat': self.fat,
            'calorie': self.calorie,
            'url': self.url,
        }


class Food_image(db.Model):
    __tablename__ = 'food_image'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    food_id = db.Column(db.ForeignKey('food.id'), nullable=False)
    img_src = db.Column(db.String(300), unique=True)
    file_path = db.Column(db.String(300))
    file_name = db.Column(db.String(30))
    extension = db.Column(db.String(30))

    @property
    def serialize(self):
        return{
            'id': self.id,
            'food_id': self.food_id,
            'img_src': self.img_src,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'extension': self.extension,
        }
