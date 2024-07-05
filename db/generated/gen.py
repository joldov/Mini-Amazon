from werkzeug.security import generate_password_hash
import csv, random
from faker import Faker
from datetime import datetime, timedelta
from random import randint
import random

num_users = 100
num_products = 1010
num_purchases = 600
num_product_reviews = 999
#num_seller_reviews = 1000
num_carts = 200

Faker.seed(0)
fake = Faker()

user_buys_products_dict = {}
user_buys_from_seller_dict = {}

seller_products = {}
seller_product_info = {}

#list of indexes corrosponding to users and sellers for use in inventory/reviews

#populated after Users.csv is created
userIndexes = []

#translate into csv for non-hashed passwords for easy log in
plainPasswords = []

# Define the range of years
current_year = datetime.utcnow().year
start_date = datetime(current_year, 1, 1)
end_date = datetime.utcnow()

# options for status of purchase
statii = ['delivered','pending','shipped']

# inputs first user that can be used for demonstration purposes
sample_user = ['0','icecream@tastes.good','Joey Shmoey','pbkdf2:sha256:600000$iWirzpRn6TZ06fFJ$e144c75055ed8adcd48e9fdb46388bde9c279a3b5ffb642b6ceaec5446c4b51e','1234 NoWhere Ln','0.00','1']

import datetime
start_date = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
end_date = datetime.datetime(2023, 11, 18, tzinfo=datetime.timezone.utc)

valid_product_review_ids = []
product_review_upvote_tuples = []

def get_csv_writer(f):
   return csv.writer(f, dialect='unix')

def gen_users(num_users):
    available_sids = []
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            if uid == 0:
                writer.writerow(sample_user)
            else:
                profile = fake.profile()
                email = profile['mail']
                plain_password = f'pass{uid}'
                password = generate_password_hash(plain_password)
                full_name = profile['name']
                balance = str(random.uniform(0.0,100.0))
                address = str(randint(1,40)) + " NoWhere Ln"
                seller = str(randint(0,1)) if uid > 0 else 1
                if seller:
                    available_sids.append(uid)
                writer.writerow([uid,email,full_name,password,address,balance,seller])
        print(f'{num_users} generated')
    return available_sids

def nonSellersList():
    userFile = open("Users.csv", "r")
    userData = list(csv.reader(userFile, delimiter=","))
    userFile.close()

    for line in userData:
        if line[-1] == '0':
            userIndexes.append(int(line[0]))
    return None

def gen_products(num_products, available_sids):
    available_pids = []
    product_names = []

    for pid in range(num_products):
        product_names.append("Product " + str(pid))

    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = product_names[pid]
            descr = fake.sentence(nb_words=10)[:-1]
            image_url = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            category_id = fake.random_int(max=5)
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            seller_id = fake.random_element(elements=available_sids)
            writer.writerow([pid, name, descr, image_url, price, category_id, available, seller_id])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_purchases(num_purchases, available_pids, available_sids):

    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users - 1)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_element(elements=available_sids)
            time_purchased = fake.date_time_between_dates(start_date, end_date)
            amount = str(random.uniform(1.0, 200.0))
            number = str(randint(1, 20))
            status = statii[randint(0, 2)]
            writer.writerow([id, uid, pid, sid, time_purchased, amount, number, status])

            # Populate user_buys_products_dict
            if uid not in user_buys_products_dict:
                user_buys_products_dict[uid] = []
            user_buys_products_dict[uid].append(pid)

        print(f'{num_purchases} generated')

#2nd one:
def gen_product_reviews(num_product_reviews, num_products):
    product_review_tuples = {}
    min_reviews_per_product=4

    with open('Review_Of_Product.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product Reviews...', end=' ', flush=True)

        id = 0
        while len(product_review_tuples) < num_products * min_reviews_per_product:
            uid = fake.random_int(min=0, max=num_users)  # random user writing review

            # check if the user has made purchases
            if uid not in user_buys_products_dict:
                continue

            # generate pid from 1 to num_products
            pid = fake.random_int(min=1, max=num_products - 5)

            # Ensure each product has at least min_reviews_per_product reviews
            if (uid, pid) not in product_review_tuples:
                product_review_tuples[(uid, pid)] = 1
            else:
                product_review_tuples[(uid, pid)] += 1

                # Skip if the product has reached the minimum required reviews
                if product_review_tuples[(uid, pid)] > min_reviews_per_product:
                    continue

            rating = fake.random_int(min=0, max=5)
            typeshit = fake.random_element(elements=("seller", "product"))
            review = fake.paragraph(nb_sentences=2)
            time_reviewed = fake.date_time_between(start_date=start_date, end_date=end_date)
            num_votes = fake.random_int(min=1, max=50)

            valid_product_review_ids.append(id)
            writer.writerow([id, uid, pid, rating, typeshit, review, time_reviewed, num_votes, ""])
            id += 1

            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)

        print(f'{id} generated')


def gen_seller_reviews(available_sids):
    with open('Review_Of_Seller.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Reviews...', end=' ', flush=True)

        id = 0
        for user in userIndexes:
            how_many_reviews = random.randint(5, 15)
            sellersToReview = random.sample(available_sids, how_many_reviews)
            for seller in sellersToReview:
                rating = fake.random_int(min=1, max=5)
                review = fake.paragraph(nb_sentences=4)
                time_reviewed = fake.date_time()
                writer.writerow([id, user, seller, rating, review, time_reviewed])
                id+=1
                if id % 100 == 0:
                    print(f'{id}', end=' ', flush=True)

        print(f'{id} generated')

def gen_inventory(num_products, available_sids):
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)

        total = 0
        for seller in available_sids:
            how_many_products = random.randint(10, 50)
            product_list = random.sample(range(0, num_products), how_many_products)

            for pid in product_list:
                quantity = random.randint(1, 999)
                price_per_item = random.randint(1, 1000)
                writer.writerow([seller, pid, quantity, price_per_item])

                if seller not in seller_products:
                    seller_products[seller] = []
                seller_products[seller].append(pid)
                seller_product_info[seller,pid] = [quantity, price_per_item]

                total += 1
                if total % 100 == 0:
                    print(f'{total}', end=' ', flush=True)
    
        print(f'{total} generated')

def gen_carts(num_users, available_sids):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for id in range(num_carts):
            if id % 10 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            sid = fake.random_element(elements=available_sids)
            seller_pids = seller_products[sid]
            pid = fake.random_element(elements=seller_pids)
            product_info = seller_product_info[sid, pid]
            description = fake.paragraph(nb_sentences=1)
            quantity = product_info[0]
            unit_price = product_info[1]
            total = quantity * unit_price
            saved = randint(0,1)
            writer.writerow([id,uid,description,pid,quantity,unit_price,total,sid,saved])
        print(f'{num_carts} generated')
    return

available_sids = gen_users(num_users)
nonSellersList()
available_pids = gen_products(num_products, available_sids)
gen_purchases(num_purchases, available_pids, available_sids)

gen_product_reviews(num_product_reviews, num_products)
gen_seller_reviews(available_sids)

gen_inventory(num_products, available_sids)

gen_carts(num_users, available_sids)