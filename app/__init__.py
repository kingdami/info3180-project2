from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = " i have made a quite random key"
app.config['TOKEN_SECRET'] = " now i have made a super secret token string"


#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wisher:pa$$word123@localhost/wishlist"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://pivebiapvavsjx:3dff4b87aee77f51fd0e10cad60c8cb7e7e84d5883f488c473a89b3bb16155a6@ec2-54-225-119-223.compute-1.amazonaws.com:5432/dec6ebeupie39d"

db = SQLAlchemy(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views