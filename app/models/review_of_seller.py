from flask import current_app as app

class Review_Of_Seller:
    def __init__(self, id, rater_id, seller_id, rating, review, time_reviewed):
        self.id = id
        self.rater_id = rater_id
        self.seller_id = seller_id
        self.rating = rating
        self.review = review
        self.time_reviewed = time_reviewed

    def get_review(id):
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Seller
WHERE id = :id
""",
                              id=id)
        return Review_Of_Seller(*(rows[0])) if rows else None
    
    def get_review_of_seller(rater_id, seller_id):

        rows = app.db.execute("""
SELECT *
FROM Review_Of_Seller
WHERE rater_id = :rater_id AND seller_id = :seller_id
""", rater_id = rater_id, seller_id = seller_id)
        print("rows is", rows)
        if len(rows) != 0:
            print("returning rows!", rows)
            return [Review_Of_Seller(*rows[0])]
        return None


    def submit_or_add_seller_review(rater_id, seller_id, rating, review, time_reviewed):
        #First check to see if the rater actually bought something from that seller_id
        try:
            rows = app.db.execute("""
    SELECT *
    FROM Purchases 
    WHERE uid = :uid AND seller_id = :seller_id
    """,
                                    uid = rater_id,
                                    seller_id = seller_id)
            
        except Exception as e:
            print(str(e))
            return None
            
        if len(rows) == 0: #if the rater hasn't actually bought something from that seller_id, return None
            print('rater', rater_id, 'has not bought anything from seller', seller_id)
            return None
        #otherwise, check if there is already a rating for that seller from that rater
        try:
                rows = app.db.execute("""
    SELECT *
    FROM Review_Of_Seller
    WHERE rater_id = :rater_id AND seller_id = :seller_id
    """,
                                    rater_id = rater_id,
                                    seller_id = seller_id)
        except Exception as e:
            print(str(e))
            return None
        if len(rows) == 0: #if there doesn't exist a review for that seller from that rater
            print('submitting new review!')
            rows = app.db.execute("""
    INSERT INTO Review_Of_Seller(rater_id, seller_id, rating, review, time_reviewed)
    VALUES(:rater_id, :seller_id, :rating, :review, :time_reviewed)
    RETURNING id
    """,
                                    rater_id = rater_id,
                                    seller_id = seller_id,
                                    rating = rating, review = review, time_reviewed = time_reviewed)
        
            #otherwise, there is already a review for this product from that user, and we need to update the table instead
        try:
            print('updating current review!')
            rows = app.db.execute("""
    UPDATE Review_Of_Seller
    SET rating = :rating, review = :review, time_reviewed = :time_reviewed
    WHERE rater_id = :rater_id AND seller_id = :seller_id
    RETURNING id
    """,
                                    rater_id = rater_id,
                                    seller_id = seller_id,
                                    rating = rating, review = review, time_reviewed = time_reviewed)
            id = rows[0][0]
        except Exception as e:
            print(str(e))
            return None

    def get_all_reviews_of_seller(sid):
        try:
            rows = app.db.execute('''
            SELECT * FROM Review_Of_Seller
            WHERE seller_id=:sid
            ''',sid=sid)
            return [Review_Of_Seller(*row) for row in rows] if rows else None
        except Exception as e:
            print(str(e))
            return None