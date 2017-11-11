import json
import random
import string

import httplib2
import requests
from flask import request, flash, g, make_response
from flask import session as login_session
from flask_httpauth import HTTPTokenAuth
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import exc

from helpers.Session import session
from model.User import User

auth = HTTPTokenAuth(scheme='Token')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Nanodegreee Udacity "


def refresh_user_state():
    state = ''
    for x in range(32):
        state += random.choice(string.ascii_uppercase + string.digits)
    login_session['state'] = state
    return state


def get_user_info(token=None, email=None):
    if token:
        try:
            return session.query(User).filter_by(token=token).one()
        except exc.SQLAlchemyError:
            return False
    elif email:
        try:
            return session.query(User).filter_by(email=email).one()
        except exc.SQLAlchemyError:
            return False
    else:
        return False


@auth.verify_token
def verify_token():
    if login_session.get('access_token'):
        g.current_user = login_session.get('access_token')
        return True
    else:
        return False


def gconnect():
    print("AEAWEW")
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # stored_access_token = login_session.get('access_token')
    # stored_gplus_id = login_session.get('gplus_id')
    # if stored_access_token is not None and gplus_id == stored_gplus_id:
    #     response = make_response(json.dumps('Current user is already connected.'),
    #                              200)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    check_user = get_user_info(None, data['email'])
    if not check_user:
        user = User(
            name=data['name'],
            picture=data['picture'],
            email=data['email'],
            token=login_session['access_token']
        )
        session.add(user)
        session.commit()
    else:
        check_user.token = login_session['access_token']
        session.add(check_user)
        session.commit()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output


def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(login_session['access_token'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)

        response.headers['Content-Type'] = 'application/json'
        return response
