from flask import (render_template, request, flash, redirect, url_for, jsonify)
from flask_login import current_user
from flask import Flask, send_file
from flask import Blueprint
import flask_paginate
from flask_paginate import Pagination, get_page_parameter

#import the python obj connected to the db
from .models.review_of_seller import Review_Of_Seller
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)

#get a particular sellers inventory
@bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if current_user.is_authenticated:
        sellerCheck = Inventory.isSeller(current_user.id)
        if sellerCheck[0][0]:
            inventory = Inventory.getInventory(current_user.id)
            inventoryLength = len(inventory)
            orders = Inventory.getOrders(current_user.id)
            ordersLength = len(orders)

            itemsperpage = 5
            page = request.args.get('page', type=int, default=1)

            pagination = Pagination(page=page, total=inventoryLength, per_page=itemsperpage, bs_version=4)
            offset = (page - 1)*itemsperpage
            inventoryChunk = inventory[offset:offset+itemsperpage]

            paginationOrders = Pagination(page=page, total=ordersLength, per_page=itemsperpage, bs_version=4)
            offset = (page - 1)*itemsperpage
            ordersChunk = orders[offset:offset+itemsperpage]

            return render_template('inventory.html',
                            inventory=inventoryChunk,
                            pagination = pagination,
                            orders = ordersChunk,
                            paginationOrders = paginationOrders,
                            seller_rating_aggregate=sellerRatingAnalytics(current_user.id), revenue_over_time = revenueOverTime(current_user.id))
        else:
            flash("Please register as a seller account.")
            return redirect(url_for("index.index"))
    
#get a particular sellers inventory by price
@bp.route('/inventory-by-price', methods=['GET', 'POST'])
def inventoryByPrice():
    if current_user.is_authenticated:
        sellerCheck = Inventory.isSeller(current_user.id)
        if sellerCheck[0][0]:
            inventory = Inventory.getInventoryByPrice(current_user.id)
            inventoryLength = len(inventory)
            orders = Inventory.getOrders(current_user.id)

            itemsperpage = 5
            page = request.args.get('page', type=int, default=1)

            pagination = Pagination(page=page, total=inventoryLength, per_page=itemsperpage, bs_version=4)
            offset = (page - 1)*itemsperpage
            inventoryChunk = inventory[offset:offset+itemsperpage]

            return render_template('inventory.html',
                            inventory=inventoryChunk,
                            orders = orders,
                            pagination = pagination,
                            seller_rating_aggregate=sellerRatingAnalytics(current_user.id), revenue_over_time = revenueOverTime(current_user.id))
        
#get a particular sellers inventory by quantity
@bp.route('/inventory-by-quantity', methods=['GET', 'POST'])
def inventoryByQuantity():
    if current_user.is_authenticated:
        sellerCheck = Inventory.isSeller(current_user.id)
        if sellerCheck[0][0]:
            inventory = Inventory.getInventoryByQuantity(current_user.id)
            inventoryLength = len(inventory)
            orders = Inventory.getOrders(current_user.id)

            itemsperpage = 5
            page = request.args.get('page', type=int, default=1)

            pagination = Pagination(page=page, total=inventoryLength, per_page=itemsperpage, bs_version=4)
            offset = (page - 1)*itemsperpage
            inventoryChunk = inventory[offset:offset+itemsperpage]

            return render_template('inventory.html',
                            inventory=inventoryChunk,
                            orders = orders,
                            pagination = pagination,
                            seller_rating_aggregate=sellerRatingAnalytics(current_user.id), revenue_over_time = revenueOverTime(current_user.id))
    
#get a particular sellers inventory by quantity
@bp.route('/inventory-by-search-term', methods=['GET', 'POST'])
def inventoryBySearchTerm():
    if current_user.is_authenticated:
        sellerCheck = Inventory.isSeller(current_user.id)
        if sellerCheck[0][0]:
            search_term = request.form.get('searchInventory')
            inventory = Inventory.getInventoryBySearch(current_user.id, search_term)
            inventoryLength = len(inventory)
            orders = Inventory.getOrders(current_user.id)

            itemsperpage = 5
            page = request.args.get('page', type=int, default=1)

            pagination = Pagination(page=page, total=inventoryLength, per_page=itemsperpage, bs_version=4)
            offset = (page - 1)*itemsperpage
            inventoryChunk = inventory[offset:offset+itemsperpage]

            return render_template('inventory.html',
                            inventory=inventoryChunk,
                            orders = orders,
                            pagination = pagination,
                            seller_rating_aggregate=sellerRatingAnalytics(current_user.id), revenue_over_time = revenueOverTime(current_user.id))

#update quantity of a product
@bp.route('/update-inventory-quantity/<int:seller_id>/<int:id>', methods=['POST'])
def updateInventoryQuantity(seller_id, id):
    if current_user.is_authenticated:
        if request.method == 'POST':
            quantity = request.form.get('quantity')
            if not (quantity == ''):
                if not (int(quantity) < 1):
                    Inventory.updateInventoryQuantity(id, quantity)
        return redirect(url_for('inventory.inventory', seller_id=seller_id))

#update price of a product
@bp.route('/update-inventory-price/<int:seller_id>/<int:id>', methods=['POST'])
def updateInventoryPrice(seller_id, id):
    if current_user.is_authenticated:
        if request.method == 'POST':
            price = request.form.get('price')
            if not (price == ''):
                if not (float(price) < 0):
                    Inventory.updateInventoryPrice(id, price)
        return redirect(url_for('inventory.inventory', seller_id=seller_id))

#delete a product
@bp.route('/delete-from-inventory/<int:seller_id>/<int:id>', methods=['POST'])
def deleteItemFromInventory(seller_id, id):
    if current_user.is_authenticated:
        if request.method == 'POST':
            Inventory.deleteItemFromInventory(id)
        return redirect(url_for('inventory.inventory', seller_id=seller_id))

#add a new product
@bp.route('/add-item-to-inventory/<int:seller_id>', methods=['POST'])
def addItemToInventory(seller_id):
    if current_user.is_authenticated:
        if request.method == 'POST':
            name = request.form.get('name')
            descr = request.form.get('descr')
            image_url = request.form.get('image_url')
            price = request.form.get('price')
            category_id = request.form.get('category_id')
            quantity = request.form.get('quantity')
            if (int(price) > 0) and (int(quantity) >= 1):
                add = Inventory.addItemToInventory(name, descr, image_url, price, category_id, seller_id, quantity)
                if type(add) == str:
                    flash(add)
            else:
                flash("Please enter valid numbers for price and quantity.")
        return redirect(url_for('inventory.inventory', seller_id=seller_id))

#see all purchases for a particular seller
@bp.route('/orders')
def orders():
    if current_user.is_authenticated:
        orders = Inventory.getOrders(current_user.id)
        ordersLength = len(orders)

        itemsperpage = 10
        page = request.args.get('page', type=int, default=1)

        paginationOrders = Pagination(page=page, total = ordersLength, per_page = itemsperpage, bs_version=4)
        offset = (page - 1)*itemsperpage
        ordersChunk = orders[offset:offset+itemsperpage]
    else:
        orders = None
    return render_template('seller_orders.html', 
                        orders = ordersChunk,
                        paginationOrders = paginationOrders)
    
#get orders by specified attribute
@bp.route('/orders-by-x', methods=['GET', 'POST'])
def ordersByX():
    if current_user.is_authenticated:
        filter_attr = request.args.get('filter_attr')

        valid_columns = ["u.full_name", "p.name", "pur.amount", "pur.number_of_items", "pur.time_purchased", "pur.status"]
        
        # Check if the provided filter_attr is a valid column name
        if filter_attr not in valid_columns:
            flash("Invalid column name for sorting")
            redirect(url_for('inventory.orders'))
        
        orders = Inventory.getOrdersByX(current_user.id, filter_attr)
        ordersLength = len(orders)

        itemsperpage = 10
        page = request.args.get('page', type=int, default=1)

        paginationOrders = Pagination(page=page, total=ordersLength, per_page=itemsperpage, bs_version=4)
        offset = (page - 1) * itemsperpage
        ordersChunk = orders[offset:offset + itemsperpage]
    else:
        orders = None

    return render_template('seller_orders.html',
                           orders=ordersChunk,
                           paginationOrders=paginationOrders)

#get a particular sellers orders by search term
@bp.route('/orders-by-search-term', methods=['GET', 'POST'])
def ordersBySearchTerm():
    if current_user.is_authenticated:
        search_term = request.form.get('searchOrders')
        orders = Inventory.getOrdersBySearch(current_user.id, search_term)
        ordersLength = len(orders)
 
        itemsperpage = 10
        page = request.args.get('page', type=int, default=1)

        paginationOrders = Pagination(page=page, total=ordersLength, per_page=itemsperpage, bs_version=4)
        offset = (page - 1)*itemsperpage
        ordersChunk = orders[offset:offset+itemsperpage]
    else:
        orders = None

    return render_template('seller_orders.html', 
                        orders = ordersChunk,
                        paginationOrders = paginationOrders)

#change fullfillment status
@bp.route('/change-fullfillment-status/<int:purchase_id>', methods=["POST"])
def changeOrderStatus(purchase_id):
    Inventory.changeFullfillmentStatus(purchase_id)
    return redirect(url_for('inventory.orders'))

#get a sellers average start rating
def sellerRatingAnalytics(seller_id):
    if current_user.is_authenticated:
        sellerReviews = Review_Of_Seller.get_all_reviews_of_seller(seller_id)

        if sellerReviews != None:
            ratingList = []
            for review in sellerReviews:
                ratingList.append(review.rating)

            totalRatings = len(ratingList)
            ratingAggregate = []
            for num in range(1,6):
                ratingCount = ratingList.count(num)
                if ratingCount != 0:
                    ratingAggregate.append(ratingCount/totalRatings)
                else:
                    ratingAggregate.append(0)
            return str(ratingAggregate)
        else:
            return "[]"
        
#analytics of revenue per month for a seller
def revenueOverTime(seller_id, time = 12):
    orders = Inventory.getOrders(seller_id)
    moneyPerMonthList = [0 for x in range(13)]
    for order in orders:
        orderFormatted = (order.amount).strip('$').replace(',', '')
        month = int(str(order.time_purchased).split("-")[1])
        moneyPerMonthList[month] += float(orderFormatted[1:])
    
    return moneyPerMonthList[1:]   