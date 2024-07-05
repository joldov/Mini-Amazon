from flask import current_app as app

from werkzeug.security import generate_password_hash
import csv, random
from faker import Faker
from random import randint
import random

from flask import current_app as app

num_users = 100
num_carts = 200

Faker.seed(0)
fake = Faker()

class Cart:
    def __init__(self,id,user_id, product,product_id,quantity, unit_price,total_price,seller,saved_for_later):
        self.id = id
        self.user_id = user_id
        self.product = product
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.seller = seller
        self.saved_for_later = saved_for_later
    
    @staticmethod
    def get_cart_item(id):
        rows = app.db.execute('''
        SELECT * FROM Carts WHERE id=:id
        ''', id=id)
        return Cart(*rows[0])

    @staticmethod
    def get_items_in_cart(user_id):
        rows = app.db.execute('''
            SELECT id,user_id,product,product_id, quantity, unit_price, 
            total_price, seller,saved_for_later 
            FROM Carts
            WHERE user_id = :user_id
            AND saved_for_later = 0
            ''',
                            user_id = user_id)
        return [Cart(*row) for row in rows]
    
    @staticmethod 
    def get_saved_for_later(user_id):
        rows = app.db.execute("""
        SELECT id,user_id,product,product_id, quantity, unit_price, 
        total_price, seller,saved_for_later
        FROM Carts
        WHERE user_id = :user_id
        AND saved_for_later = 1
        """, 
                    user_id = user_id)
        return [Cart(*row) for row in rows]

    
 
    @staticmethod
    def list_items(user_id):
        rows = app.db.execute('''
            SELECT product_id
            FROM Carts
            WHERE user_id =  :user_id
        ''', 
                    user_id = user_id)
        return [int(rows[i][0]) for i in range(len(rows))]

    @staticmethod
    def add_item_to_cart(user_id, product_id, seller_id):

        rows = app.db.execute('''
        SELECT name, price FROM Products
        WHERE id = :product_id
        ''', product_id=product_id)

        p_name = rows[0][0]
        price_per_item = float((rows[0][1]))

        query = """
        INSERT INTO Carts (user_id, product ,product_id, quantity, unit_price, total_price, seller, saved_for_later)
        VALUES (:user_id, :p_name, :p_id, 1, :ppi, :ppi, :sid, 0) """

        app.db.execute(query, user_id = user_id, p_name=p_name, p_id=product_id, ppi=price_per_item, sid=seller_id)

    @staticmethod        
    def remove_item_from_cart(cart_id):
        app.db.execute("""
        DELETE FROM Carts
        WHERE id = :cart_id
        """,
                cart_id = cart_id)
    
    @staticmethod
    def increment_quantity(product_id):
        app.db.execute("""
        UPDATE Carts
        SET quantity = quantity + 1, total_price = total_price + unit_price
        WHERE product_id = :product_id
        """,
                product_id = product_id)
    
    @staticmethod
    def decrement_quantity(cart_id):
        app.db.execute("""
        UPDATE Carts
        SET quantity = quantity - 1, total_price = total_price - unit_price
        WHERE id = :cart_id
        """,
                cart_id = cart_id)

    @staticmethod
    def submit_order(uid,pid,sid,time,price,quantity,status):
        try:
            app.db.execute('''
            INSERT INTO Purchases(uid,pid,sid,time_purchased,amount,number_of_items,status)
            VALUES (:uid,:pid,:sid,:time,:price,:quantity,:status)
            ''', uid=uid,pid=pid,sid=sid,time=time,price=price,quantity=quantity,status=status)
        except Exception as e:
            print(str(e))
        
    @staticmethod
    def get_item_availability(seller_id, product_id, quantity):
        rows = app.db.execute("""
        SELECT quantity
        FROM Products
        WHERE seller_id = :seller_id
        AND id = :product_id
        """,
                seller_id = seller_id, product_id = product_id)
        
        if not rows:
            availible_quant = 0
        else:
            availible_quant = rows[0][0]
        
        return availible_quant
    

    @staticmethod
    def add_to_saved_for_later(cart_id):
       app.db.execute("""
        UPDATE Carts
        SET saved_for_later = 1
        WHERE id = :cart_id
        """,
                cart_id = cart_id)
    

    @staticmethod
    def move_back_to_cart(cart_id):
        app.db.execute("""
        UPDATE Carts
        SET saved_for_later = 0
        WHERE id = :cart_id
        """,
                cart_id = cart_id)

    @staticmethod
    def get_cart_item_id(product_id,seller_id):
        rows = app.db.execute("""
        SELECT id
        FROM Carts 
        WHERE product_id = :product_id
        AND seller = :seller_id
        """,
                    product_id = product_id,
                    seller_id = seller_id)
        return int(rows[0][0])
    
    @staticmethod
    def decr_inventory(product_id,seller_id, decr):
        app.db.execute("""
        UPDATE Products
        SET quantity = quantity - :decr
        WHERE id = :product_id
        AND seller_id = :seller_id
        """,
                    product_id = product_id,
                    seller_id = seller_id,
                    decr = decr)
    
    @staticmethod
    def get_balance(user_id):
        rows = app.db.execute("""
        SELECT balance
        FROM Users
        WHERE id = :user_id
        """,
                    user_id = user_id)
        return (float(rows[0][0][1:]))
    
        
    
        
    

    
    



