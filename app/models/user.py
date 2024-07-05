from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, full_name, address, balance):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
        SELECT password, id, email, full_name, address, balance
        FROM Users
        WHERE email = :email
        """,
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
        SELECT email
        FROM Users
        WHERE email = :email
        """,
                              email=email)
        return len(rows) > 0

    # inputs info from registration flask form to database
    @staticmethod
    def register(email, password, full_name, address, seller):
        try:
            rows = app.db.execute("""
            INSERT INTO Users(email, full_name, password, address, balance, seller)
            VALUES(:email, :full_name, :password, :address, :balance, :seller)
            RETURNING id
            """,
                                  email=email,
                                  full_name=full_name,
                                  password=generate_password_hash(password),
                                  address=address,
                                  balance=0.00,
                                  seller=seller)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    # returns User object for given id        
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
        SELECT id, email, full_name, address, balance
        FROM Users
        WHERE id = :id
        """,
                              id=id)
        return User(*(rows[0])) if rows else None

    # return 1 if User is seller; 0 otherwise
    @staticmethod
    def seller_bool(id):
        rows = app.db.execute('''
        SELECT seller FROM Users WHERE id=:id
        ''',id=id)
        seller = rows[0][0]
        return seller

    # returns all users, sorted by id
    @staticmethod
    def get_all_users():
        rows = app.db.execute("""SELECT id, email, full_name, address, balance FROM Users""")
        res = [User(*row) for row in rows]
        ret = sorted(res, key=lambda user: user.id)
        return ret

    # returns all users, sorted by name alphabetically
    @staticmethod
    def get_all_users_by_name():
        rows = app.db.execute('''SELECT id, email, full_name, address, balance FROM Users''')
        res = [User(*row) for row in rows]
        ret = sorted(res, key=lambda user: user.full_name)
        return ret

    # returns balance for given User id
    @staticmethod
    def get_bank_info(id):
        try:
            rows = app.db.execute('''
            SELECT balance FROM Users
            WHERE id=:id
            ''',id=id)
            balance = rows[0][0]
            return balance
        except Exception as e:
            print(str(e))
            return None

    # withdraws from balance the given amount
    @staticmethod
    def decr_bank_info(id,decr):
        try:
            rows = app.db.execute('''
            UPDATE Users SET balance=balance-:decr WHERE id=:id
            ''', decr=decr,id=id)
        except Exception as e:
            print(str(e))
            return None
    
    # deposits to balance the given amount
    @staticmethod
    def incr_bank_info(id,incr):
        try:
            rows = app.db.execute('''
            UPDATE Users SET balance=balance+:incr WHERE id=:id
            ''', incr=incr,id=id)
        except Exception as e:
            print(str(e))
            return None

    # replaces current name with the given one
    @staticmethod
    def update_name(id,new_name):
        try:
            rows = app.db.execute('''
            UPDATE Users SET full_name=:new WHERE id=:id
            ''', new=new_name, id=id)
        except Exception as e:
            print(str(e))
            return None

    # replaces current address with the given one
    @staticmethod
    def update_address(id,new_addr):
        try:
            rows = app.db.execute('''
            UPDATE Users SET address=:new WHERE id=:id
            ''', new=new_addr, id=id)
        except Exception as e:
            pritn(str(e))
            return None

    # replaces current passowrd with the given one, using a hashing technique
    @staticmethod
    def update_password(id,new_pass):
        try:
            rows = app.db.execute('''
            UPDATE Users SET password=:new WHERE id=:id
            ''', new=generate_password_hash(new_pass), id=id)
        except Exception as e:
            print(str(e))
            return None

    # replaces current email with the given one
    @staticmethod
    def update_email(id,new_email):
        try:
            rows = app.db.execute('''
            UPDATE Users SET email=:new WHERE id=:id
            ''', new=new_email, id=id)
        except Exception as e:
            print(str(e))
            return None

    # returns full_name, address, and email
    @staticmethod
    def get_profile(id):
        try:
            rows = app.db.execute('''
            SELECT full_name, address, email
            FROM Users WHERE id=:id
            ''', id=id)
            return rows[0]
        except Exception as e:
            print(str(e))
            return None

    # updates normal user account to be seller account
    @staticmethod
    def become_seller(id):
        try:
            rows = app.db.execute('''
            UPDATE Users SET seller=true WHERE id=:id
            ''', id=id)
        except Exception as e:
            print(str(e))
            return None