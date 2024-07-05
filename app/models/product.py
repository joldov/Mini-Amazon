from flask import current_app as app

from sqlalchemy import exc

class Product:
    def __init__(self, id, name, descr, image_url, price, category_id, available, seller_id, quantity):
        self.id = id
        self.name = name
        self.descr = descr
        self.image_url = image_url
        self.price = price
        self.category_id = category_id
        self.available = available
        self.seller_id = seller_id
        self.quantity = quantity

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.id = :id
AND products.category_id = cat.id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.available = :available
AND products.category_id = cat.id
''',
                              available=available)
        return [Product(*row) for row in rows]

    @staticmethod
    def get_limit(limit, available=True):
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.available = :available
AND products.category_id = cat.id

''',
                              available=available)
        return [Product(*(rows[i])) for i in range(limit,limit+10)]

    @staticmethod
    def get_keyword(keyword):
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.name LIKE :keyword
OR products.descr LIKE :keyword
AND products.category_id = cat.id
''',

                        keyword='%' + keyword + '%')

        return [Product(*row) for row in rows]

    @staticmethod
    def get_category(cat):
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, caty.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS caty
WHERE caty.cat_name = :cat
AND products.category_id = caty.id
''',

                        cat=cat)

        return [Product(*row) for row in rows]

    @staticmethod
    def get_expensive():
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.category_id = cat.id
ORDER BY products.price DESC

''')

        return [Product(*row) for row in rows]

    @staticmethod
    def get_cheap():
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, cat.cat_name, products.available, products.seller_id, products.quantity
FROM Products AS products, Categories AS cat
WHERE products.category_id = cat.id
ORDER BY products.price
''')

        return [Product(*row) for row in rows]

    @staticmethod
    def get_review():
        rows = app.db.execute('''
SELECT products.id, products.name, products.descr, products.image_url, products.price, products.category_id, products.available, products.seller_id, products.quantity
FROM Products AS products, Review_Of_Product AS review
WHERE products.id = review.pid
GROUP BY products.id, products.name, products.descr, products.image_url, products.price, products.category_id, products.available, products.seller_id, products.quantity
ORDER BY AVG(review.rating) DESC
''')

        return [Product(*row) for row in rows]

    
    @staticmethod
    def add(cat_name):
        try:
            rows = app.db.execute('''
INSERT INTO Categories(cat_name)
VALUES (:cat_name)
''',
    cat_name = cat_name)
        except exc.DataError:
            return "Must have values entered in all fields."

