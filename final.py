#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import desc

from helpers.Auth import auth, gconnect, gdisconnect, login_session,\
    get_user_info, refresh_user_state
from helpers.Session import session
from model.CatalogItem import CatalogItem
from model.Category import Category

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config.from_object(__name__)


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
        return render_template('/category/categoryDetails.html',
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
            session.add(check_item)
            session.commit()
        else:
            new_item = CatalogItem(
                name=request.form['name'],
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
        session.delete(item_to_delete)
        return redirect(
            url_for('list_category', category_id=category_id), code=302)


# ITEM DETAILS
@app.route("/catalog/<string:category_name>/items/<int:item_id>")
def list_item(item_id):
    # Render page listing a selected item
    scope_item = session.query(
        CatalogItem).filter_by(
        id=item_id
    ).all()
    return render_template('/item/itemDetails.html',
                           item=scope_item,
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
