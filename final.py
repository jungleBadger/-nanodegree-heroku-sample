#!/usr/bin/env python3
import json
import random
import string
import datetime
import httplib2
import requests
from flask import Flask, render_template, redirect, jsonify, url_for
from flask import request, flash, g, make_response
from flask import session as login_session
from flask_httpauth import HTTPTokenAuth
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config.from_object(__name__)
Base = declarative_base()

engine = create_engine('sqlite:///store.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)

session = DBSession()


#


class User(Base):
    __tablename__ = 'user'
    name = Column(
        String(30),
        nullable=False
    )

    picture = Column(
        String(150),
        nullable=True
    )

    email = Column(
        String(40),
        primary_key=True
    )

    token = Column(
        String(40),
        primary_key=True
    )


class Category(Base):
    __tablename__ = 'category'
    name = Column(
        String(30),
        nullable=False
    )

    description = Column(
        String(150),
        nullable=True
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    name = Column(
        String(80),
        nullable=False
    )

    author = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer,
        primary_key=True
    )

    description = Column(String(250))

    price = Column(String(8))

    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    category_id = Column(
        Integer,
        ForeignKey('category.id')
    )

    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'created_date': self.created_date
        }


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
def verify_token(token):
    if login_session.get('access_token'):
        print(token)
        g.current_user = login_session.get('access_token')
        return True
    else:
        return False


def check_author(email):
    return login_session['email'] == email


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
    #     response = make_response(
    #         json.dumps('Current user is already connected.'),
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
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(login_session['access_token'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(
        login_session['access_token'])
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

        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)

        response.headers['Content-Type'] = 'application/json'
        return response


# ROOT PATH
@app.route('/home')
@app.route('/')
def home():
    categories = session.query(Category).all()
    items = session.query(CatalogItem).order_by(
        desc(CatalogItem.created_date)).limit(10)
    return render_template('home.html',
                           user=get_user_info(
                               login_session.get('access_token')),
                           categories=categories,
                           items=items,
                           STATE=refresh_user_state())


# LOG IN USING GOOGLE PROVIDER
@app.route('/gconnect', methods=['POST'])
def connect():
    return gconnect()


# LOGOUT FROM GOOGLE PROVIDER
@app.route('/logout', methods=['GET', 'POST'])
def disconnect():
    return gdisconnect()


# INSERT NEW CATEGORY
@app.route("/category/new", methods=["GET", "POST"])
@auth.login_required
def category():
    # If POST will insert new category - else will serve the HTML
    if request.method == 'POST':
        new_category = Category(name=request.form['name'])
        session.add(new_category)
        session.commit()
        return redirect(url_for('home'), code=302)
    else:
        return render_template('category/newCategory.html',
                               user=get_user_info(
                                   login_session.get('access_token')),
                               STATE=refresh_user_state())


# LIST CATEGORY DETAILS BY ID
@app.route("/category/<int:category_id>/info", methods=["GET"])
def list_category(category_id):
    scope_category = session.query(Category).filter_by(id=category_id).one()
    if scope_category:
        items = session.query(CatalogItem).filter_by(
            category_id=scope_category.id).all()
        print(get_user_info(login_session.get('access_token')))
        return render_template('category/categoryDetails.html',
                               user=get_user_info(
                                   login_session.get('access_token')),
                               category=scope_category,
                               items=items,
                               STATE=refresh_user_state()
                               )
    else:
        return "Invalid query"


# INSERT/UPDATE A NEW ITEM INTO CATEGORY BY ID / PROVIDES THE PAGE
@app.route("/category/<int:category_id>/item/new", methods=["GET", "POST"])
@auth.login_required
def item(category_id):
    if request.method == 'POST':
        if request.form['item_id']:
            check_item = session.query(CatalogItem).filter_by(
                id=request.form['item_id']).one()
            check_item.name = request.form['name']
            check_item.description = request.form['description']
            check_item.price = request.form['price']
            if check_author(check_item.author):
                session.add(check_item)
                session.commit()
            else:
                return "Unauthorized"

        else:
            new_item = CatalogItem(
                name=request.form['name'],
                author=get_user_info(
                    login_session.get('access_token')
                ).email,
                description=request.form['description'],
                price=request.form['price'],
                category_id=category_id)
            session.add(new_item)
            session.commit()
        return redirect(
            url_for('list_category', category_id=category_id), code=302)
    else:
        categories = session.query(Category).all()
        return render_template('/item/newItem.html',
                               user=get_user_info(
                                   login_session.get('access_token')),
                               categories=categories,
                               STATE=refresh_user_state())


# DELETE CATALOG ITEM BY ID
@app.route(
    "/category/<int:category_id>/item/<int:item_id>/delete", methods=["POST"])
@auth.login_required
def delete_item(category_id, item_id):
    # Delete Category Item by ID
    if request.method == 'POST':

        item_to_delete = session.query(CatalogItem).filter_by(id=item_id).one()
        print(item_to_delete.author)
        if check_author(item_to_delete.author):
            session.delete(item_to_delete)
            session.commit()
        else:
            return "Unauthorized"
        return redirect(
            url_for('list_category', category_id=category_id), code=302)


# NEW ITEM (PAGE AND HANDLER)
@app.route("/item/new", methods=["GET", "POST"])
def add_item():
    # Delete Category Item by ID
    if request.method == 'POST':
        category_id = request.form["category_id"]
        new_item = CatalogItem(
            name=request.form['name'],
            author=get_user_info(
                login_session.get('access_token')
            ).email,
            description=request.form['description'],
            price=request.form['price'],
            category_id=category_id)
        session.add(new_item)
        session.commit()

        return redirect(
            url_for('home'), code=302)
    else:
        categories = session.query(Category).all()
        return render_template('/item/newItem.html',
                               categories=categories,
                               user=get_user_info(
                                   login_session.get('access_token')),
                               STATE=refresh_user_state())


# JSON REST ENDPOINTS

# List all categories
@app.route('/categories/v1/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# List Items from a Category by ID
@app.route('/category/<int:category_id>/v1/JSON')
def category_json(category_id):
    # List a Category by ID
    items = session.query(CatalogItem).filter_by(
        category_id=category_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])


# List a CatalogItem by ID
@app.route('/item/<int:item_id>/v1/JSON')
def catalog_item_json(item_id):
    catalog_item = session.query(CatalogItem).filter_by(id=item_id).one()
    return jsonify(Menu_Item=catalog_item.serialize)


# List all items
@app.route('/items/v1/JSON')
def items_json():
    items = session.query(CatalogItem).all()
    return jsonify(items=[r.serialize for r in items])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
