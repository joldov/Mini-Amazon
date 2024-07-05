from flask import current_app as app

class Review_Of_Product:
    def __init__(self, id, uid, pid, rating, typeshit, review, time_reviewed, num_votes, imagepath):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.rating = rating
        self.typeshit = typeshit
        self.review = review
        self.time_reviewed = time_reviewed
        self.num_votes = num_votes
        self.imagepath = imagepath

# fetch a review
    def get_review(id):
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE id = :id
""",
                              id=id)
        return Review_Of_Product(*(rows[0])) if rows else None

# milestone 2: getting 5 most recent reviews
    def get_5_latest_reviews(uid):
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE uid = :uid
ORDER BY time_reviewed DESC
""",
                                  uid = uid)
        if rows is not None and len(rows) > 5:
            return [Review_Of_Product(*rows[i]) for i in range(5)]

        return [Review_Of_Product(*row) for row in rows] if rows else None


# get your reviews sorted by its number of upvotes from greatest to least
    def sort_reviews_by_votes(uid):
        rows = app.db.execute("""
            SELECT *
            FROM Review_Of_Product
            WHERE uid = :uid
            ORDER BY num_votes DESC
        """, uid = uid)
        return [Review_Of_Product(*row) for row in rows] if rows else None

# get all reviews posted by this user
    def get_all_reviews(uid):
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE uid = :uid
ORDER BY time_reviewed DESC
""",
                                  uid = uid)
        return [Review_Of_Product(*row) for row in rows] if rows else None
    
# get review for a product
    def get_review_of_product(uid, pid):
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE uid = :uid AND pid = :pid
""", uid = uid, pid = pid)
        if len(rows) != 0:
            return [Review_Of_Product(*rows[0])]
        return None

# get every single review left on a single product
    def get_all_reviews_product(pid):
        '''
        Get all reviews for a product given a product id
        '''
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE pid = :pid
ORDER BY time_reviewed DESC
""",
        pid = pid)
        return [Review_Of_Product(*row) for row in rows] if rows else None

# main function that adds or edits reviews
    def submit_or_add_review(uid, pid, rating, typeshit, review, time_reviewed):
        '''
        Submit a review or add one, depending on if there is already a review
        '''
        if Review_Of_Product.get_review_of_product(uid, pid) is None: #If there is no review yet, insert it into the table
            try:
                rows = app.db.execute("""
    INSERT INTO Review_Of_Product(uid, pid, rating, typeshit, review, time_reviewed)
    VALUES(:uid, :pid, :rating, :typeshit, :review, :time_reviewed)
    RETURNING id
    """,
                                    uid = uid,
                                    pid = pid,
                                    rating = rating, typeshit = typeshit, review = review, time_reviewed = time_reviewed)
                id = rows[0][0]
                return Review_Of_Product.get_review(id)
            except Exception as e:
                print(str(e))
                return None
        else:
            # else edit the existing review
            try:
                rows = app.db.execute("""
    UPDATE Review_Of_Product
    SET rating = :rating, typeshit = :typeshit, review = :review, time_reviewed = :time_reviewed
    WHERE uid = :uid AND pid = :pid
    RETURNING id
    """,
                                    uid = uid,
                                    pid = pid,
                                    rating = rating, typeshit = typeshit, review = review, time_reviewed = time_reviewed)
                id = rows[0][0]
                return Review_Of_Product.get_review(id)
            except Exception as e:
                print(str(e))
                return None
    
# delete your review
    def remove_review_of_product(uid, pid):
        rows = app.db.execute("""
        DELETE
        FROM Review_Of_Product
        WHERE uid = :uid AND pid = :pid
        """, uid = uid, pid = pid)
        return None

#average product and seller reviews
    def product_reviews_with_avg(uid):
            '''
            Get product ids of all products along with their average ratings
            '''
            rows = app.db.execute("""
    SELECT uid, AVG(rating) AS avg_rating
    FROM Review_Of_Product
    WHERE uid = :uid
    GROUP BY uid
    """, uid=uid)

            if len(rows) != 0:
                avg_rating = round(float(rows[0][1]), 2)
                return avg_rating

            return None

# nums of reviews
    def user_number_of_ratings(uid):
        '''
        Get the number of ratings for a user
        '''
        rows = app.db.execute("""
        SELECT COUNT(*) AS num_ratings
        FROM Review_Of_Product
        WHERE uid = :uid
        """, uid=uid)
        if rows:
            num_ratings = rows[0][0] 
            return num_ratings
        return None

# upvote and downvote stuff below
    def add_upvote(rater_id, product_review_id):
        '''
        Add an upvote to a review
        '''
   
        rows = app.db.execute("""
            INSERT INTO User_Upvotes_Product_Review(rater_id, product_review_id)
            VALUES(:rater_id, :product_review_id)
            RETURNING id
        """,
        rater_id=rater_id,
        product_review_id=product_review_id
        )
        app.db.execute("""
            UPDATE Review_Of_Product
            SET num_votes = num_votes + 1
            WHERE id = :product_review_id
        """, product_review_id=product_review_id)
        
        return True
    
    def get_product_id_for_review(product_review_id):
        '''
        Get the product id for a review
        '''
        rows = app.db.execute("""
        SELECT pid 
        FROM Review_Of_Product
        WHERE id = :product_review_id 
        """, product_review_id = product_review_id)
        return rows[0][0]
   
    def remove_upvote(rater_id, product_review_id):
        '''
        Remove an upvote from a review
        '''
        rows = app.db.execute("""
            DELETE FROM User_Upvotes_Product_Review
            WHERE rater_id = :rater_id AND product_review_id = :product_review_id
        """, rater_id=rater_id, product_review_id=product_review_id)
            
        app.db.execute("""
            UPDATE Review_Of_Product
            SET num_votes = num_votes - 1
            WHERE id = :product_review_id
        """, product_review_id=product_review_id)
            
        return True

    def is_upvoted_by(product_review_id, uid):
        '''
        Return True or False whether or not a user has already upvoted a review
        '''
        rows = app.db.execute("""
SELECT *
FROM User_Upvotes_Product_Review
WHERE rater_id = :uid AND product_review_id = :review_id
""", uid = uid, review_id = product_review_id)
        print('in is_upvoted by function, rater_id is', uid, 'and product_review_id is', product_review_id)
        if len(rows) == 0:
            return False
        return True

# get the number of upvotes a review has
    def get_upvote_count(product_review_id):
        rows = app.db.execute("""
            SELECT num_votes
            FROM Review_Of_Product
            WHERE id = :product_review_id
        """, product_review_id=product_review_id)
        return rows[0][0] if rows else 0

# get number of reviews left on a single product
    def get_num_of_reviews_for_product(product_id):
        rows = app.db.execute("""
        SELECT COUNT(*) 
        FROM Review_Of_Product
        WHERE pid = :product_id
        GROUP BY pid
        """, product_id = product_id)
        if len(rows) != 0:
            return rows[0][0]
        return 0

# remove your image attached to your revieww
    def remove_image_from_product_review(product_review_id):
        '''
        Disassociate an image from a product review
        '''
        rows = app.db.execute("""
    UPDATE Review_Of_Product
    SET imagepath = :imagepath
    WHERE id = :product_review_id
    """,
                                    product_review_id = product_review_id, imagepath = "")

# change the image attached to your review
    def replace_image(product_review_id, imagepath):
        '''
        Replace an image with a different image
        '''
        rows = app.db.execute("""
    UPDATE Review_Of_Product
    SET imagepath = :imagepath
    WHERE id = :product_review_id
    """,
                                    imagepath = imagepath, product_review_id = product_review_id)

# get all the reviews left by a user (you)
    def get_all_product_reviews_for_user(rater_id):
        '''
        Get all product reviews for a user with id rater_id
        '''
        rows = app.db.execute("""
SELECT *
FROM Review_Of_Product
WHERE uid = :rater_id
ORDER BY time_reviewed DESC
""", rater_id = rater_id)
        if len(rows) != 0:
            return [Review_Of_Product(*row) for row in rows]
        return None

# top 3 most upvoted reviews on a product
    @staticmethod
    def get_top_3_most_popular_reviews(pid):
        '''
        Get the top 3 product reviews with the most votes
        '''
        rows = app.db.execute('''
            SELECT *
            FROM Review_Of_Product
            WHERE pid = :pid
            ORDER BY num_votes DESC, time_reviewed DESC
            LIMIT 3
            ''', pid=pid)
    

        return  [Review_Of_Product(*row) for row in rows] if rows else None
    
# pagination function for reviews
    @staticmethod
    def get_all_reviews_paginated(uid, page, per_page):
        offset = (page - 1) * per_page
        rows = app.db.execute("""
            SELECT *
            FROM Review_Of_Product
            WHERE uid = :uid
            ORDER BY time_reviewed DESC
            LIMIT :per_page OFFSET :offset
        """, uid=uid, per_page=per_page, offset=offset)

        return [Review_Of_Product(*row) for row in rows] if rows else None