#!/usr/bin/env python3
import random
import string
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from helpers.Session import session
from helpers.Auth import auth, gconnect, gdisconnect, g, login_session
from model.Category import Category
from model.CatalogItem import CatalogItem

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config.from_object(__name__)
app.url_map.strict_slashes = False


@app.route('/')
@app.route('/home')
@auth.login_required
def showRestaurants():
    categories = session.query(Category).all()
    # return "This will be our public home page"
    print(g.current_user)
    return render_template('home.html', categories=categories)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def connect():
    return gconnect()


@app.route('/logout', methods=['GET', 'POST'])
def disconnect():
    return gdisconnect()


@app.route("/category/new", methods=["GET", "POST"])
def category():
    # If POST will insert new category - else will serve the HTML
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('/home'))
    else:
        return render_template('newCategory.html')


@app.route("/item/new", methods=["GET", "POST"])
def item(category_id):
    # If POST will insert new item - else will serve the HTML

    ## validate if category exhists
    if request.method == 'POST':
        newItem = CatalogItem(name=request.form['name'],
                              description=request.form['description'],
                              price=request.form['price'],
                              category_id=category_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('/home'))
    else:
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)






@app.route("/catalog/<string:category_name>/items", methods=["GET"])
def listCategory(category_name):
    # Render page listing a selected category
    category = session.query(Category).filter_by(name=category_name).one()
    if category:
        items = session.query(CatalogItem).filter_by(
            category_id=category.get('id')).all()
        return render_template('categoryDetails.html', category=category, items=items)
    else:
        return "Invalid query"


@app.route("/catalog/<string:category_name>/items/<int:item_id>")
def listItem(item_id):
    # Render page listing a selected item
    item = session.query(CatalogItem).filter_by(
        id=item_id).all()
    return render_template('itemDetails.html', item=item)








# JSON REST ENDPOINTS

@app.route('/category/<int:category_id>/v1/JSON')
def categoryJSON(category_id):
    # List a Category by ID
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(
        category_id=category_id).all()
    return jsonify(CatalogItem=[i.serialize for i in items], Category=category)


@app.route('/category/<int:category_id>/item/<int:item_id>/v1/JSON')
def catalogItemJSON(category_id, item_id):
    # List a CatalogItem by ID
    Catalog_Item = session.query(CatalogItem).filter_by(id=item_id).one()
    return jsonify(Menu_Item=Catalog_Item.serialize)


@app.route('/categories/v1/JSON')
def categoriesJSON():
    # List all categories
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/items/v1/JSON')
def itemsJSON():
    # List all items
    items = session.query(CatalogItem).all()
    return jsonify(items=[r.serialize for r in items])



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)