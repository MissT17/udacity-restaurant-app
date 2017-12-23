from flask import Blueprint
from flask import session as login_session
import random
import string
from flask import Flask, render_template
from flask import request, redirect, url_for, jsonify, flash
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy.orm import sessionmaker
from database_setup_fn import Base, Restaurant, MenuItem, User
from sqlalchemy import create_engine


login = Blueprint('login', __name__)
engine = create_engine('sqlite:///restaurantmenu_fn_users.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open(
    'client_secret_new.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant project udacity"


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def getUserID(email):
    try:
        user = session.query(User).\
            filter_by(email=login_session['email']).one()
        return user.id
    except:
        return None


@login.route('/login')
def showLogin():
    # create a state variable
    state = ' '.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@login.route('/gconnect', methods=['POST'])
def gconnect():
    # verify if the connection between the server and
    # the client is not compromized
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data  # retrieve the one-time code from Google
    try:
        # create a FLOW object required by Google to exchange
        # a one-time code to access_token
        oauth_flow = flow_from_clientsecrets(
            'client_secret_new.json',
            scope=''
        )
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # retrieve an access_token to enable the requests from server to Google
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)  # NOQA
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID"),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # store the access token, if it already exists as variable
    stored_access_token = login_session.get('access_token')
    # store the user, if he already exists as variable
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # create a login session with all the information
    # related to the session and user
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    user_id = getUserID(login_session['email'])
    if user_id == None:
        user_id = createUser(login_session)
    else:
        login_session['user_id'] = user_id
    output = ''  # prepare the html response page
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src='' '
    output += login_session['picture']
    output += ' " style="width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;">'  # NOQA
    flash("You are now logged in as %s" % login_session['username'])
    return output


@login.route('/fbconnect', methods=['POST'])
def fbconnect():
    # verify if the connection between the server and
    # the client is not compromized
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dump('Invalid state parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # retrieve one-time code for connection with Facebook
    access_token = request.data
    app_id = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/v2.8/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # userinfo_url = "https://graph.facebook.com/v2.8/me"
    # retrieve access_token for communication between
    # server and Facebook directly
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['access_token'] = token
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''  # prepare the html response page
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src='' '
    output += login_session['picture']
    output += ' " style="width:300px; height:300px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;">'  # NOQA
    flash("you are now logged in as %s" % login_session['username'])
    return output


# code that is executed whenever the user disconnects(Google or Facebook)
@login.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['access_token']
        flash(
            "You have been successfully logged out,"
            " navigate the website and login to modify its content")
        return redirect(url_for('showallrestaurants'))
    else:
        flash("You were not logged in to begin with")
        return redirect(url_for('showallrestaurants'))


@login.route('/gdisconnect')  # Google specific disconnect operations
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user is not connected'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content_Type'] = 'application/json'
        # flash("You have been successfully logged out,
        # navigate the website and login to modify its content")
        return redirect('/restos')
    else:
        response = make_response(
            json.dumps('Failed to revoke for given user'),
            400
        )
        response.headers['Content-Type'] = 'application/json'
        return response


@login.route('/fbdisconnect')  # Facebook specific disconnect operations
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out"

