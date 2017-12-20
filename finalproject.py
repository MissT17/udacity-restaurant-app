from flask import Flask, render_template
from flask import request, redirect, url_for, jsonify, flash
from json_format import serialize, serialize_resto, serialize_item
from sqlalchemy import create_engine
from database_setup_fn import Base, Restaurant, MenuItem, User
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from login import login
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
# create Blueprint to split the login (routes) of the app into 2
# files(login.py contains logic for authrntication process, finalproject.py
# contains the authorization and content logic)
app.register_blueprint(login)
engine = create_engine('sqlite:///restaurantmenu_fn_users.db')
Base.metadata.bind = engine

UPLOAD_FOLDER = './static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


DBSession = sessionmaker(bind=engine)
session = DBSession()

# the route allows to access pages that display all restaurants available
#  in the database. One view is available for logged in and the other
#  for logged out users.


@app.route('/')
@app.route('/restos/')
def showallrestaurants():
    restaurants = session.query(Restaurant).order_by(Restaurant.name).all()
    if 'username' not in login_session:
        return render_template('public_allrestos.html', restos=restaurants)
    else:
        user = session.query(User).\
            filter_by(name=login_session['username']).one()
        return render_template('allrestos.html', restos=restaurants, user=user)


# routes that allow to execute various actions with
# restaurants (add, edit or delete them)

@app.route('/restos/new', methods=['GET', 'POST'])
def createNewResto():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        file_img = request.files['file']
        filename = secure_filename(file_img.filename)
        file_img.save(os.path.join(UPLOAD_FOLDER, filename))
        filename_full = './static/images/' + filename
        new_image = Image.open(filename_full)
        new_image.thumbnail((500, 400))
        img_url_resize = filename[:-4] + '_thumb.jpg'
        new_image.save(os.path.join(UPLOAD_FOLDER, img_url_resize))
        resized_url = '/static/images/' + img_url_resize
        user = session.query(User). \
            filter_by(name=login_session['username']).one()
        new_resto = Restaurant(
            image=resized_url,
            name=request.form['name'],
            description=request.form['description'],
            user_id=user.id
        )
        # print new_resto.image
        session.add(new_resto)
        session.commit()
        flash("The restaurant has been added to the list fof restaurants.")
        return redirect(url_for('showallrestaurants'))
    return render_template('addresto.html')


@app.route('/restos/<int:resto_id>/edit', methods=['GET', 'POST'])
def editResto(resto_id):
    restaurant = session.query(Restaurant).filter_by(id=resto_id).one()
    name_resto = restaurant.name
    description_resto = restaurant.description
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            restaurant.description = request.form['description']
            file_img = request.files['file']
            filename = secure_filename(file_img.filename)
            file_img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/static/images/' + filename
            restaurant.image = img_url
            session.add(restaurant)
            session.commit()
            return redirect(url_for('showallrestaurants'))
    else:
        return render_template(
            'editresto.html',
            resto_identif=resto_id,
            name_resto=name_resto,
            resto_desc=description_resto
        )


@app.route('/restos/<int:resto_id>/delete', methods=['GET', 'POST'])
def deleteResto(resto_id):
    resto_to_delete = session.query(Restaurant).filter_by(id=resto_id).one()
    resto_name = resto_to_delete.name
    user = session.query(User).filter_by(name=login_session['username']).one()
    if 'username' not in login_session:
        return redirect('/login')
    if resto_to_delete.user_id != user.id:
        flash("You are not allowed to delete this content")
        return redirect(url_for('showallrestaurants'))
    if request.method == 'POST':
        session.delete(resto_to_delete)
        session.commit()
        flash("The restaurant %s has been deleted" % resto_name)
        return redirect(url_for('showallrestaurants'))
    return render_template(
        'deleteresto.html',
        resto=resto_id,
        resto_name=resto_to_delete.name
    )


# routes that display the list of menu items in a restaurant.
# Two views are available:
# one for logged in (with possibility to edit & delete items) and the other
# for logged out users (only able to consult the content)

@app.route('/restos/<int:resto_ID>', methods=['GET', 'POST'])
@app.route('/restos/<int:resto_ID>/menu')
def restoMenu(resto_ID):
    resto = session.query(Restaurant).filter_by(id=resto_ID).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=resto_ID).all()
    name_resto = resto.name
    user = session.query(User).filter_by(name=login_session['username']).one()
    if 'username' not in login_session:
        return render_template(
            'public_resto_menu.html',
            resto_identif=resto_ID,
            menu=menu,
            name_resto=name_resto
        )
    elif resto.user_id != user.id:
            return render_template(
                'public_resto_menu.html',
                resto_identif=resto_ID,
                menu=menu,
                name_resto=name_resto
            )
    else:
        if menu == []:
            return redirect(url_for('addNewMenuItem', resto_id=resto_ID))
        return render_template(
            'resto_menu.html',
            resto_identif=resto_ID,
            menu=menu,
            name_resto=name_resto,
            creator=resto.user_id
        )


# routes that allow to execute various
# actions with menu items (add, edit or delete them)

@app.route(
    '/restos/<int:resto_id>/menu/<int:item_id>/edit',
    methods=['GET', 'POST']
    )
def editMenuItems(resto_id, item_id):
    item = session.query(MenuItem).filter_by(id=item_id).one()
    item_name = item.name
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
            item.description = request.form['description']
            item.price = request.form['price']
            item.course = request.form['course']
            session.add(item)
            session.commit()
            return redirect(url_for('restoMenu', resto_ID=resto_id))
    else:
        return render_template(
            'edit_menu_item.html',
            price=item.price,
            course=item.course,
            resto=resto_id,
            item=item_id,
            item_name=item_name,
            item_description=item.description
        )


@app.route('/restos/<int:resto_id>/menu/new', methods=['GET', 'POST'])
def addNewMenuItem(resto_id):
    resto = session.query(Restaurant).filter_by(id=resto_id).one()
    resto_name = resto.name
    if request.method == 'POST':
        added_item = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            restaurant_id=resto_id,
            user_id=resto.user_id
        )
        session.add(added_item)
        session.commit()
        return redirect(url_for('restoMenu', resto_ID=resto_id))
    return render_template(
        'add_menu_item.html',
        resto=resto_id,
        resto_name=resto_name
    )


@app.route(
    '/restos/<int:resto_id>/menu/<int:item_id>/delete',
    methods=['GET', 'POST']
)
def deleteMenuItem(resto_id, item_id):
    res = session.query(Restaurant).filter_by(id=resto_id).one()
    resto_name = res.name
    item_to_delete = session.query(MenuItem).filter_by(id=item_id).one()
    item_name = item_to_delete.name
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('restoMenu', resto_ID=resto_id))
    return render_template(
        'delete_menu_item.html',
        resto=resto_id,
        item=item_id,
        item_name=item_name,
        resto_name=resto_name
    )


# following routes provide access to different types
# of information in JSON format(list of restaurants,
# menu items in a restaurant or a menu item)

@app.route('/restos/<int:resto_ID>/menu/JSON')
def restoMenuJSON(resto_ID):
    menu = session.query(MenuItem).filter_by(restaurant_id=resto_ID).all()
    if menu != []:
        return jsonify(MenuItems=[item.serialize for item in menu])
    else:
        print 'No menu items'


@app.route('/restos/JSON')
def listrestoJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(
        Restaurants=[restaurant.serialize for restaurant in restaurants]
    )


@app.route('/restos/<int:resto_id>/menu/<int:item_id>/JSON')
def menuItem(resto_id, item_id):
    restaurant = session.query(Restaurant).filter_by(id=resto_id).one()
    item = session.query(MenuItem).filter_by(id=item_id).one()
    return jsonify(MenuItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    
