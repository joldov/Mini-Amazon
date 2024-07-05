from flask import render_template
from flask_login import current_user
import datetime
from humanize import naturaltime
import math

from .models.product import Product
from .models.purchase import Purchase
from .models.feedback import Feedback
from .models.user import User


from flask import Blueprint
bp = Blueprint('index', __name__)

# converts time to comprehensible format
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:e
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(current_user.id)
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)

# get list of purchases, sorted by most recent by default
@bp.route('/history/<int:page>')
def history(page):
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(current_user.id)
        per_page = 10
        total = len(purchases)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(purchases):
            page_purchs = purchases[start:]
            stop = len(purchases)
        else:
            page_purchs = purchases[start:stop]
        return render_template('purchase.html',purchase_history=page_purchs,number=page,pages=pages,
                               start=start+1,stop=stop,total=total,humanize_time=humanize_time)
    else:
        return render_template('purchase.html',purchase_history=None,number=None,pages=None)

# get list of purchases, sorted by name alphabetically
@bp.route('/history_by_name/<int:page>')
def history_by_name(page):
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_by_name(current_user.id)
        per_page = 10
        total = len(purchases)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(purchases):
            page_purchs = purchases[start:]
            stop = len(purchases)
        else:
            page_purchs = purchases[start:stop]
        return render_template('purchase_by_name.html',purchase_history=page_purchs,number=page,pages=pages,
                               start=start+1,stop=stop,total=total,humanize_time=humanize_time)
    else:
        return render_template('purchase_by_name.html',purchase_history=None,number=None,pages=None)

# get list of purchases, sorted by price ASC
@bp.route('/history_by_price/<int:page>')
def history_by_price(page):
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_by_price(current_user.id)
        per_page = 10
        total = len(purchases)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(purchases):
            page_purchs = purchases[start:]
            stop = len(purchases)
        else:
            page_purchs = purchases[start:stop]
        return render_template('purchase_by_price.html',purchase_history=page_purchs,number=page,pages=pages,
                               start=start+1,stop=stop,total=total,humanize_time=humanize_time)
    else:
        return render_template('purchase_by_price.html',purchase_history=None,number=None,pages=None)

# get list of purchases, grouped by status (delivered, pending, shipped)
@bp.route('/history_by_status/<int:page>')
def history_by_status(page):
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_by_status(current_user.id)
        per_page = 10
        total = len(purchases)
        pages = math.ceil(total/per_page)
        start = page*per_page - per_page
        stop = start+per_page
        if stop >= len(purchases):
            page_purchs = purchases[start:]
            stop = len(purchases)
        else:
            page_purchs = purchases[start:stop]
        return render_template('purchase_by_status.html',purchase_history=page_purchs,number=page,pages=pages,
                               start=start+1,stop=stop,total=total,humanize_time=humanize_time)
    else:
        return render_template('purchase_by_status.html',purchase_history=None,number=None,pages=None)

# renders the order page for given purchase
@bp.route('/order/<int:oid>/<int:page>/<sort>')
def order_page(oid,page,sort):
    if current_user.is_authenticated:
        purchase = Purchase.get(oid)
        seller = User.get(purchase.sid).full_name
        return render_template('order_page.html',purchase=purchase,page=page,sort=sort,seller=seller)
    else:
        return render_template('order_page.html')

# retrieves expenses spend on purchases and displays in a chart in html page
@bp.route('/purchase_analytics/<int:uid>', methods=['GET','POST'])
def purchase_analytics(uid):
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(uid)
        expenses = [float(purchase.amount.strip('$')) for purchase in purchases]
        statuses = [purchase.status for purchase in purchases]
        return render_template('purchase_analytics.html', expenses=expenses, statuses=statuses)

