from flask import Flask
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,instance_relative_config=True)
app.config.from_pyfile('config.py',silent=False)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "bashumar291@gmail.com"
app.config['MAIL_PASSWORD'] = "efriwdvzhvxuiowm"
mail = Mail(app)
db = SQLAlchemy(app)

from footifyapp import adminroutes, userroutes