from flask import render_template
from flask_login import current_user
from flask import redirect, url_for
import datetime
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.purchase import Purchase
from .models.user import User
from .models.review_of_product import Review_Of_Product
from flask import Blueprint
from flask import jsonify
from flask import request

bp = Blueprint('products', __name__)


@bp.route('/products')
def products():
    # get all available products for sale:
    products = Product.get_all(True)
    
    # render the page
    # return jsonify([product.__dict__ for product in products])
    return render_template('product.html',
                           avail_products=products)

# displays all the reviews associated with a product and shows top 3 most upvoted reviews at the top 
# the rest of the reviews are still displayed at the bottom of the top 3
@bp.route('/products/<int:k>',methods=['GET'])
def product_page(k):
    product = Product.get(k)
    reviews = Review_Of_Product.get_all_reviews_product(k) 
    top_3_reviews = Review_Of_Product.get_top_3_most_popular_reviews(k)
    num_of_reviews = Review_Of_Product.get_num_of_reviews_for_product(k)
    
    return render_template('product.html',
                            product=product, reviews = reviews, top_3_reviews = top_3_reviews, num_of_reviews = num_of_reviews)


@bp.route('/products/list/<int:limit>',methods=['GET'])
def product_list(limit):
    fix_limit = limit
    if limit < 10:
        fix_limit = 10
    if limit > 2000:
        fix_limit = 2000
    products = Product.get_limit(fix_limit)

    return render_template('list.html',
                            avail_products=products,
                            limit = fix_limit)

@bp.route('/products/search')
def product_search():
    return render_template('search.html')

@bp.route('/products/search/keyword/',methods=['GET','POST'])
def search_keyword():
    
    keyword = request.form.get('keyword')
    products = Product.get_keyword(keyword)

    return render_template('list.html',
                        avail_products=products,
                        limit = 10)

@bp.route('/products/search/category/',methods=['GET','POST'])
def search_category():
    
    category = request.form.get('category')
    

    products = Product.get_category(category)

    return render_template('list.html',
                        avail_products=products,
                        limit = 10)

@bp.route('/products/search/price/',methods=['GET','POST'])
def search_price():
    
    expensive = request.form.get('prices')

    match expensive:
        case "Most Expensive":
            products = Product.get_expensive()
        case "Least Expensive":
            products = Product.get_cheap()

    # render the page
    # return jsonify([product.__dict__ for product in products])
    return render_template('list.html',
                           avail_products=products,
                           limit = 10)

@bp.route('/products/search/review/',methods=['GET','POST'])
def search_review():
    products = Product.get_review()

    return render_template('list.html',
                           avail_products=products,
                           limit = 10)


@bp.route('/products/category')
def category():
    return render_template('category.html')

#add a new category
@bp.route('/products/category', methods=['POST'])
def add_category():
    if request.method == 'POST':
        cat_name = request.form.get('cat_name')
        add = Product.add(cat_name)
        if type(add) == str:
            flash(add)
    return redirect(url_for('products.category'))

