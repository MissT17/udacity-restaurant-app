from flask import Blueprint
from sqlalchemy import create_engine
from database_setup_fn import Base
from sqlalchemy.orm import sessionmaker


login = Blueprint('login', __name__)
engine = create_engine('sqlite:///restaurantmenu_fn_users.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()