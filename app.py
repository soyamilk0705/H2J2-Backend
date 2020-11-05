from flask import Flask
from flask import render_template
from models import db
from flask_cors import CORS

app = Flask(__name__, template_folder='../H2J2-Front', static_folder='../H2J2-Front/assets')
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register')
def register():
    pass


@app.route('/control')
def control():
    pass


@app.route('/login')
def login():
    pass


@app.route('/logout')
def logout():
    pass


@app.route('/detail')
def detail():
    pass


@app.route('/adminadd')
def adminadd():
    pass


@app.route('/admin')
def admin():
    pass


# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://" 
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
# app.config['SECRET_KEY'] = 'sdfsdfsdddf'
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30) # 세션유지 시간을 30분으로 지정

# db.init_app(app)
# db.app = app
# db.create_all()

if __name__ == '__main__':
    app.run()

# host='127.0.0.1', port=5000, debug=True
# host='0.0.0.0', port=5000, debug=True