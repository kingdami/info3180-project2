from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask.ext.heroku import Heroku

app = Flask(__name__)
app.config['SECRET_KEY'] = " i have made a quite random key"
app.config['TOKEN_SECRET'] = " now i have made a super secret token string"


# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wisher:pa$$word123@localhost/wishlist"
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://hqaxtohhpsvuyj:4b7f4957ddde9dccbf7f739f2496d5a9d5a66c5535aab2a981a0480bb657472e@ec2-54-163-252-55.compute-1.amazonaws.com:5432/d21p31bgba74om'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning

# DATABASE_URL='postgres://hqaxtohhpsvuyj:4b7f4957ddde9dccbf7f739f2496d5a9d5a66c5535aab2a981a0480bb657472e@ec2-54-163-252-55.compute-1.amazonaws.com:5432/d21p31bgba74om'
# app.config['HEROKU_POSTGRESQL_CHARCOAL_URL']='postgres://nzeedrfyktybgw:401b9e8328a019b0c413c786985ce3a9a9df8a7035cf9f0ff83c564098b7cab3@ec2-184-73-236-170.compute-1.amazonaws.com:5432/dadursdb5ouqav'
heroku = Heroku(app)
db = SQLAlchemy(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views