from flask import Blueprint
from sqlalchemy import create_engine
from database_setup_fn import Base, Restaurant, MenuItem, User
from sqlalchemy.orm import sessionmaker
from flask import session as login_session

login = Blueprint('login', __name__)
engine = create_engine('sqlite:///restaurantmenu_fn_users.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
print 'ok'