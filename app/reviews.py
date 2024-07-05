from flask import render_template
from flask_login import current_user 
from flask import redirect, url_for, flash, request
import datetime
from .models.product import Product
from .models.purchase import Purchase
from .index import history
#from .models.message import Message
from .models.review_of_product import Review_Of_Product
from .models.review_of_seller import Review_Of_Seller
from wtforms import IntegerField, SubmitField, StringField
from flask import jsonify
from flask_wtf import FlaskForm
import os
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import math
from flask import Blueprint
bp = Blueprint('reviews', __name__)

from flask import Flask, send_file

# flask form that takes in all the review inputs 
class ReviewForm(FlaskForm):
    new_review = StringField('New Review', validators=[DataRequired()])
    new_rating = IntegerField('New Rating', validators=[DataRequired()])
    new_type = StringField('Seller or Product', validators=[DataRequired()])
    submit = SubmitField('Add Review')
# flask form that deletes reviews
class DeleteForm(FlaskForm):
    submit_delete = SubmitField('Delete')

# main reviews function that takes all input from user and adds that review into database
@bp.route('/reviews', methods=['GET','POST'])
def reviews(): 
    form = ReviewForm()
    newReview = form.new_review.data
    newRating = form.new_rating.data
    newType = form.new_type.data

    if form.validate_on_submit():
        return redirect(url_for('reviews.all_reviews', uid = uid))
    return render_template('5_reviews.html', form=form)

# fetch all reviews of a single user and adds pagination:
@bp.route('/reviews/<int:uid>')
def all_reviews(uid):
    products = Product.get_all(True)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    reviews = Review_Of_Product.get_all_reviews(uid)
    
    total = len(reviews)
    pages = math.ceil(total / per_page)
    start = page*per_page - per_page
    stop = start + per_page

    if stop >= len(reviews):
        page_reviews = reviews[start:]
        stop = len(reviews)
    else:
        page_reviews = reviews[start:stop]
    user_avg_rating = Review_Of_Product.product_reviews_with_avg(uid)
    num_ratings = Review_Of_Product.user_number_of_ratings(uid)
    

    return render_template('5_reviews.html', avail_products=products, user_avg_rating=user_avg_rating, num_ratings=num_ratings, reviews=page_reviews, number=page, pages=pages, start=start + 1, stop=stop, total=total)

# deleting reviews:
@bp.route('/delete_product_review/<int:uid>/<int:product_id>', methods=['GET','POST'])
def delete_product_review(uid, product_id):
    Review_Of_Product.remove_review_of_product(uid, product_id)
    return redirect(url_for('reviews.all_reviews', uid=current_user.id))

# adding and editing reviews:
@bp.route('/reviews/<int:uid>/<int:product_id>', methods=['GET', 'POST'])
def look_at_product_review_and_edit_product_review(uid, product_id):
    product_review = Review_Of_Product.get_review_of_product(uid, product_id)
    
    form = ReviewForm()
    newReview = form.new_review.data
    newRating = form.new_rating.data
    newType = form.new_type.data

    if form.validate_on_submit():
        time_reviewed = datetime.datetime.now()
    
        Review_Of_Product.submit_or_add_review(uid, product_id, newRating, newType, newReview, time_reviewed)
        return redirect(url_for('reviews.all_reviews', uid=current_user.id))

    delete_form = DeleteForm()

    if delete_form.validate_on_submit():
        Review_Of_Product.remove_review_of_product(uid, product_id)
        return redirect(url_for('reviews.all_reviews', uid=current_user.id))

    return render_template('submit_product_review.html', product_review=product_review, uid = uid, product_id = product_id, delete_form=delete_form, form=form)

# upvote functionality for both upvoting and downvoting reviews
@bp.route('/products/<int:product_id>/reviews/<int:product_review_id>/upvote/<int:rater_id>', methods=['POST'])
def add_or_remove_upvote(product_id, product_review_id, rater_id):
    upvote_count = Review_Of_Product.get_upvote_count(product_review_id)
    product = Product.get(product_id)
    reviews = Review_Of_Product.get_all_reviews_product(product_id)
    top_3_reviews = Review_Of_Product.get_top_3_most_popular_reviews(product_id)

    if Review_Of_Product.is_upvoted_by(product_review_id, rater_id):
        Review_Of_Product.remove_upvote(rater_id, product_review_id)
        upvote_count = Review_Of_Product.get_upvote_count(product_review_id)
    else:
        Review_Of_Product.add_upvote(rater_id, product_review_id)
        upvote_count = Review_Of_Product.get_upvote_count(product_review_id)

    return render_template('product.html', product=product, reviews=reviews, top_3_reviews = top_3_reviews)

# uploading images to reviews function:
@bp.route('/upload_photo/<int:product_review_id>', methods=['GET', 'POST'])
def upload_photo(product_review_id):
    review = Review_Of_Product.get_review(product_review_id)  

    if request.method == 'POST':   
        f = request.files['file'] 
        filepath = os.path.join("app/static",f.filename)
        f.save(filepath)
        Review_Of_Product.replace_image(product_review_id,"/static/"+str(f.filename)) 
        return redirect(url_for('reviews.look_at_product_review_and_edit_product_review', uid = review.uid, product_id = review.pid))
    return redirect(url_for('reviews.look_at_product_review_and_edit_product_review', uid = review.uid, product_id = review.pid))
    
# remove an image that you already have attached from your review without having to delete your entire review
@bp.route('/delete_photo/<int:product_review_id>', methods=['GET', 'POST'])
def remove_image_from_prod_review(product_review_id):
    review = Review_Of_Product.get_review(product_review_id)
    Review_Of_Product.remove_image_from_product_review(product_review_id)
    return redirect(url_for('reviews.look_at_product_review_and_edit_product_review', uid = review.uid, product_id = review.pid))

# sort your reviews by number of upvotes from greatest to least
@bp.route('/reviews-by-upvotes', methods=['GET', 'POST'])
def reviewsbyUpvotes():
    uid = current_user.id
    num_ratings = Review_Of_Product.user_number_of_ratings(uid)
    reviews = Review_Of_Product.get_all_reviews(uid)
    sortedReviews = Review_Of_Product.sort_reviews_by_votes(uid)
    print(sortedReviews)

    products = Product.get_all(True)
    page = request.args.get('page', 1, type=int)
    per_page = num_ratings

    total = len(sortedReviews)
    pages = math.ceil(total / per_page)
    start = page * per_page - per_page
    stop = start + per_page

    if stop >= len(sortedReviews):
        page_reviews = sortedReviews[start:]
        stop = len(sortedReviews)
    else:
        page_reviews = sortedReviews[start:stop]

    user_avg_rating = Review_Of_Product.product_reviews_with_avg(uid)

    return render_template('5_reviews.html', sortedReviews=sortedReviews, avail_products=products, user_avg_rating=user_avg_rating, num_ratings=num_ratings, reviews=page_reviews, number=page, pages=pages, start=start + 1, stop=stop, total=total)
