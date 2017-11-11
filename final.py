#!/usr/bin/env python3
import random
import string
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from helpers.Session import session
from helpers.Auth import auth, gconnect, gdisconnect, g, login_session, get_user_info, refresh_user_state
from model.Category import Category
from model.CatalogItem import CatalogItem

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config.from_object(__name__)

@app.route('/home')
@app.route('/')
def home():
    categories = session.query(Category).all()
    # return "This will be our public home page"
    print(login_session.get('access_token'))
    return render_template('home.html',
                           user=get_user_info(login_session.get('access_token')),
                           categories=categories,
                           STATE=refresh_user_state())


@app.route('/gconnect', methods=['POST'])
def connect():
    return gconnect()


@app.route('/logout', methods=['GET', 'POST'])
def disconnect():
    return gdisconnect()


@app.route("/category/new", methods=["GET", "POST"])
@auth.login_required
def category():
    # If POST will insert new category - else will serve the HTML
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('home'), code=302)
    else:
        return render_template('category/newCategory.html',
                               user=get_user_info(login_session.get('access_token')),
                               STATE=refresh_user_state())


@app.route("/category/<int:category_id>/item/new", methods=["GET", "POST"])
@auth.login_required
def item(category_id):
    # If POST will insert new item - else will serve the HTML

    ## validate if category exhists
    if request.method == 'POST':
        if request.form['item_id']:
            check_item = session.query(CatalogItem).filter_by(id=request.form['item_id']).one()
            check_item.name = request.form['name']
            check_item.description = request.form['description']
            check_item.price = request.form['price']
            session.add(check_item)
            session.commit()
        else:
            newItem = CatalogItem(name=request.form['name'],
                                  description=request.form['description'],
                                  price=request.form['price'],
                                  category_id=category_id)
            session.add(newItem)
            session.commit()
        return redirect(url_for('listCategory', category_id=category_id), code=302)
    else:
        categories = session.query(Category).all()
        return render_template('/item/newItem.html',
                               user=get_user_info(login_session.get('access_token')),
                               categories=categories,
                               STATE=refresh_user_state())




@app.route("/category/<int:category_id>/item/<int:item_id>/delete", methods=["POST"])
@auth.login_required
def delete_item(category_id, item_id):
    # Delete Category Item by ID
    if request.method == 'POST':
        itemToDelete = session.query(CatalogItem).filter_by(id=item_id).one()
        session.delete(itemToDelete)
        return redirect(url_for('listCategory', category_id=category_id), code=302)



@app.route("/category/<int:category_id>/info", methods=["GET"])
def listCategory(category_id):
    # Render page listing a selected category
    category = session.query(Category).filter_by(id=category_id).one()
    if category:
        items = session.query(CatalogItem).filter_by(
            category_id=category.id).all()
        return render_template('/category/categoryDetails.html',
                               user=get_user_info(login_session.get('access_token')),
                               category=category,
                               items=items,
                               STATE=refresh_user_state()
                               )
    else:
        return "Invalid query"


@app.route("/catalog/<string:category_name>/items/<int:item_id>")
def listItem(item_id):
    # Render page listing a selected item
    item = session.query(CatalogItem).filter_by(
        id=item_id).all()
    return render_template('/item/itemDetails.html',
                           item=item,
                           STATE=refresh_user_state())








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