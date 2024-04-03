from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
    
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.app_context().push()

from optimise import routes

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = 'users.login'
# login_manager.login_message_category = 'info'

# def create_app():
    # app = Flask(__name__)
    
    # app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    # db.init_app(app)
    # bcrypt.init_app(app)
    # login_manager.init_app(app)

    # from optimise import routes
    # return app



# if __name__ == '__main__':
#     app.run(debug=False)


