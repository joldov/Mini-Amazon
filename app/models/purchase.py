from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, sid, name, time_purchased, amount, number_of_items, status):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.name = name
        self.time_purchased = time_purchased
        self.amount = amount
        self.number_of_items = number_of_items
        self.status = status

    # get purchase for the given id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products AS B, Users as C
        WHERE A.id=:id AND A.pid = B.id
        ''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    # gets all purchases back to a given date
    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products AS B
        WHERE uid = :uid AND A.pid = B.id
        AND time_purchased >= :since
        ORDER BY time_purchased DESC
        ''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
    
    # gets all purchases
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products as B
        WHERE uid = :uid AND A.pid = B.id
        ORDER BY time_purchased DESC
        ''',
                              uid=uid)
        return [Purchase(*row) for row in rows]

    # gets all purchases sorted by name alphabetically
    @staticmethod
    def get_all_by_uid_by_name(uid):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products as B
        WHERE uid = :uid AND A.pid = B.id
        ORDER BY time_purchased DESC
        ''',
                              uid=uid)
        res = [Purchase(*row) for row in rows]
        ret = sorted(res, key=lambda purchase: purchase.name)
        return ret

    # gets all purchases sorted by price ASC
    @staticmethod
    def get_all_by_uid_by_price(uid):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products as B
        WHERE uid = :uid AND A.pid = B.id
        ORDER BY A.amount ASC
        ''',
                              uid=uid)
        return [Purchase(*row) for row in rows]

    # gets all purchases grouped by status (delivered, pending, shipped)
    @staticmethod
    def get_all_by_uid_by_status(uid):
        rows = app.db.execute('''
        SELECT A.id, A.uid, A.pid, A.sid, B.name, A.time_purchased, A.amount, A.number_of_items, A.status
        FROM Purchases AS A, Products as B
        WHERE uid = :uid AND A.pid = B.id
        ORDER BY A.status ASC
        ''',
                              uid=uid)
        return [Purchase(*row) for row in rows]

