from flask import current_app as app
from datetime import datetime

class Feedback:
    def __init__(self, id, uid, pid, review, rating, creation_date):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.review = review
        self.rating = rating
        self.creation_date = creation_date

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM Feedback
        WHERE id = :id
        ''', id=id)
        return Feedback(*(rows[0])) if rows else None

    @staticmethod
    def get_recent_feedback_for_user(uid, limit=5):
        rows = app.db.execute('''
        SELECT *
        FROM Feedback
        WHERE uid = :uid
        ORDER BY creation_date DESC
        LIMIT 5;
        ''', uid=uid, limit=limit)
        return [Feedback(*row) for row in rows]

    @staticmethod
    def enter_feedback(uid,review,rating):
        try:
            rows = app.db.execute('''
            INSERT INTO Feedback(uid,pid,review,rating,creation_date)
            VALUES (:uid,:pid,:review,:rating,:creation_date)
            ''',uid=uid,review=review, rating=rating)
            id = rows[0][0]
            return Review.get(id)
        except Exception as e:
            print(str(e))
            return None
