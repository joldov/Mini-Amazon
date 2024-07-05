from flask import render_template
from flask_login import current_user
from flask import jsonify,redirect,url_for,request,flash
import datetime
from datetime import datetime
from random import randint
from .models.product import Product
from .models.purchase import Purchase
from .models.user import User
from .models.carts import Cart
from flask import current_app as app


from flask import Blueprint
bp = Blueprint('carts', __name__)

statii = ['delivered','pending','shipped']

@bp.route('/cart')
def cart():
    if current_user.is_authenticated:
        cart = Cart.get_items_in_cart(current_user.id)
        return render_template("cart.html",
                            cart = cart)

    else:
        cart = None
    return redirect(url_for("users.login"))

@bp.route('/add_to_cart/<int:product_id>/<int:seller_id>/', methods=['POST'])
def add_to_cart(product_id, seller_id):
    if current_user.is_authenticated:
        if int(product_id) in Cart.list_items(current_user.id):
            Cart.increment_quantity(product_id)
            cart_item_id =  Cart.get_cart_item_id(product_id,seller_id)
            Cart.move_back_to_cart(cart_item_id)    
        else:
            Cart.add_item_to_cart(current_user.id, product_id, seller_id)
        return redirect(url_for('carts.cart'))
    else:
        return redirect(url_for('users.login'))

@bp.route("/delete_item_from_cart/<int:cart_id>",methods = ["POST"])
def delete_item_from_cart(cart_id):
    if current_user.is_authenticated:
        Cart.remove_item_from_cart(cart_id)
        return redirect(url_for('carts.cart'))
    else:
        return redirect(url_for('users.login'))

@bp.route("/increment_quantity/<int:product_id>", methods = ["POST"])
def increment_item_quantity(product_id):
    if current_user.is_authenticated:
        Cart.increment_quantity(product_id)
        return redirect(url_for('carts.cart'))

@bp.route("/decrement_quantity/<int:cart_id>/<int:quantity>", methods = ["POST"])
def decrement_item_quantity(cart_id,quantity):
    if current_user.is_authenticated:
        if quantity >1:
            Cart.decrement_quantity(cart_id)
        if quantity ==1:
            Cart.remove_item_from_cart(cart_id)
        return redirect(url_for('carts.cart'))

@bp.route('/checkout/<int:cart>', methods=['GET','POST'])
def checkout(cart):
    if current_user.is_authenticated:
        cart_item = Cart.get_cart_item(cart)
        seller = User.get(cart_item.seller).full_name
        item_availability = Cart.get_item_availability( cart_item.seller,
                                                        cart_item.product_id,
                                                        cart_item.quantity)
        min_quantity = min(item_availability, cart_item.quantity)
        price = cart_item.unit_price * min_quantity
        return render_template('checkout.html',
                                item=cart_item,
                                seller=seller,
                                item_availability = item_availability,
                                min_quantity=min_quantity,
                                price = price)

@bp.route('/submit/<int:id>/<int:uid>/<int:pid>/<int:sid>/<float:price>/<int:quantity>')
def submit_order(id,uid,pid,sid,price,quantity):
    if current_user.is_authenticated:
        if sufficient_funds(uid, price):
            time = datetime.now()
            status = statii[randint(0, 2)]
            Cart.submit_order(uid,pid,sid,time,price,quantity,status)
            Cart.remove_item_from_cart(id)
            User.decr_bank_info(uid,str(price))
            Cart.decr_inventory(pid,sid, quantity)
            return redirect(url_for('index.history', page = 1))
        return redirect(url_for("users.get_balance", uid = current_user.id))
    else:
        return redirect(url_for("users.get_balance", uid = current_user.id))

@bp.route('/checkout_all',methods=['GET', 'POST'])
def checkout_all_items():
    promo_code = request.form.get("promoCode")
    total = 0


    if current_user.is_authenticated:
        cart = Cart.get_items_in_cart(current_user.id)
        item_availability = [
                                Cart.get_item_availability(item.seller,
                                item.product_id,
                                item.quantity)
                                for item in cart
                                ]

        for item, num_avail in zip(cart, item_availability):
            total += item.unit_price * min(num_avail, item.quantity)
        
        all_items_not_available = all(item_availability[i] >= cart[i].quantity for i in range(len(cart)))

        if promo_code:
            discount = calc_discount(promo_code)
            if discount is not None:
                total -= discount
    else:
        cart = None
    return render_template("checkout_all.html",
                            cart = cart,
                            item_availability=item_availability,
                            total = total,
                            all_items_not_available=all_items_not_available
                            )

@bp.route('/submit_full_order/<int:final_total>')
def submit_full_order(final_total):
    if current_user.is_authenticated:
        if sufficient_funds(current_user.id, final_total):
            cart = Cart.get_items_in_cart(current_user.id)
            item_availability = [
                                    Cart.get_item_availability(item.seller,
                                    item.product_id,
                                    item.quantity)
                                    for item in cart
                                    ]
            for i in range(len(cart)):
                item = cart[i]
                num_avail = item_availability[i]
                final_total = item.unit_price * min(num_avail, item.quantity)
                final_quantity =  min(num_avail, item.quantity)
                submit_order_helper(item.id,item.user_id,
                                    item.product_id,
                                    item.seller,
                                    final_total,
                                    final_quantity)
                User.incr_bank_info(item.seller, str(final_total))
            User.decr_bank_info(current_user.id,str(final_total))
            return redirect(url_for('index.history', page = 1))
    return redirect(url_for('users.get_balance', uid = current_user.id))

# id,uid,pid,sid,price,quantity
@bp.route('/cart/saved_for_later')
def view_saved_for_later():
    if current_user.is_authenticated:
        saved_items = Cart.get_saved_for_later(current_user.id)
    else:
        cart = None
    return render_template("saved_for_later.html",
                            saved_items = saved_items)

@bp.route('/add_to_saved_for_later/<int:cart_id>')
def add_to_saved_for_later(cart_id):
    if current_user.is_authenticated:
        Cart.add_to_saved_for_later(cart_id)
        return redirect(url_for("carts.view_saved_for_later"))

@bp.route('/move_back_to_cart/<int:cart_id>')
def move_back_to_cart(cart_id):
    if current_user.is_authenticated:
        Cart.move_back_to_cart(cart_id)
        return redirect(url_for("carts.cart"))


def submit_order_helper(id,uid,pid,sid,price,quantity):
    time = datetime.now()
    status = statii[randint(0, 2)]
    Cart.submit_order(uid,pid,sid,time,price,quantity,status)
    Cart.remove_item_from_cart(id)
    Cart.decr_inventory(pid,sid, quantity)
    return

def calc_discount(promo_code):
    ten_percent_codes = ["TEN", "10%OFF"]
    twenty_percent_codes = ["TWENTY", "20%OFF"]
    if promo_code in ten_percent_codes:
        return 10
    elif promo_code in twenty_percent_codes:
        return 20
    else:
        return None
def sufficient_funds(user_id, total):
    funds = Cart.get_balance(user_id)
    if funds < total:
        return False
    return True
