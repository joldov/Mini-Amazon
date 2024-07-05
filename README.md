Project name: Teletubbies
Project members: Oscar Nolen, Noelle Garrick, Jessica Oldov, Rees Payne, Collin Royal

Team Members Roles:
1. Oscar Nolen: Users Guru (Accounts/Purchases)
2. Noelle Garrick: Sellers Guru (Inventory/ Order Fullfillment)
3. Jessica Oldov: Social Guru (Feedback / Messaging)
4. Rees Payne: Products Guru (Products)
5. Collin Royal: Carts Guru (Carts/Orders)

GitHub/ GitLab Repository Link: https://gitlab.oit.duke.edu/odn/teletubbies-316-project

Final Submission Video: https://drive.google.com/drive/folders/1USWqbnh1uvzgvBw9fyY9iLskDNo1PBbZ?usp=drive_link

Final Submission Updates: 

Oscar Nolen:
- Further increased the database sizes for User and Purchases
- Added pagination for purchases, as well as different sort options for purchases list
- Added emojis to website banner
- Added improved banking system that allows deposit and withdrawals, but throws error for not enough money
- Added different sort options for all users list
- Added links to order page for a given purchase
- Updated a few fields in the Purchases schema

Where to find my work:
- **Users.csv/Purchases.csv/gen.py**: added larger database
- **create.sql**: updated Purchases table schema
- **app/users.py**: added improved profile, banking, and user list functions
- **app/models/user.py**: added back end functions improved User features
- **app/index.py** : added improved purchases features including purchase list, sorting, and charts
- **app/models/purchase.py**: added back end functions for improved Purchase features

Noelle Garrick:
- Updated Products to have a larger database
- Added seller validation to make sure inventory only displays for sellers
- Added rating and revenue analytics
- Added update quantity, add product, and delete product functions to inventory 
with error catching for missing data
- Added sort and search functions to inventory and orders pages
- Added orders page to display orders of the sellers products, with a button to fullfill and denotion of fullfillment status

Where to find my work:
- **db/create.sql**: co-created products table
- **app/inventory.py**: created Inventory class and methods to add, delete, update, sort, search products and orders as well as prepare data for analytics charts
- **app/models/inventory.py**: functions for filtering and modifying the products and purchases table to support functions in app/Inventory.py
- **app/templates/inventory.html**: created page that displays the sellers inventory and rating and revenue anaytics
- **app/templates/orders.html**: created a page that displays orders associated with the seller

Jessica Oldov:
- Users can leave product/ seller reviews only for purchased products
- Can see all reviews left for each product, alongside its rating and number of upvotes
- Upvote functionality for reviews, users can upvote and downvote reviews
- Top 3 most upvoted reviews are displayed at the top of each product
- Image uploading feature for reviews; users can add and remove images for their reviews without having to delete their reviews entirely
- Pagination for all the reviews left by the user
- User's reviews can be sorted by number of upvotes in descending order

Where to find my work:
- **app/models/review_of_product.py**: wrote SQL functions for upvoting, image uploading, and fetching id's for reviews
- **app/reviews.py**: wrote routing functions for fetching and displaying product and seller reviews
- **db/create.sql**: added new table for upvote functionality, added more attributes to table in order to support new features
- **app/templates/5_reviews.html**: modified page that displays paginated view of all reviews left by the current user
- **app/templates/submit_product_review**: modified page to include pagination and image uploading functions
- **app/templates/product.html**: modified page to include all reviews for each product, with top 3 most upvoted appearing at most top of the page
- **db/generated/gen.py**: generated new data to work for modified schema that includes number of upvotes and image urls

Rees Payne:
- Updated pagination functions to prevent negative limits and reduce total page size.
- Added a search page and the functionality to search by keywords, category, price, and average review score.
- Moved full product list from index to separate list page.
- Added ability to add new categories.
- Updated detailed product page to improve design.

Where to find my work:
- **app/models/product.py**: added sorting functions
- **app/templates/product.html**: reworked design to be more visually appealing
- **app/products.py**: added search functions
- **db/create.sql**: added categories
- **db/generated/Categories.csv**: added data
- **app/templates/list.html**: updated page buttons
- **app/templates/search.html**: added search functions
- **app/templates/category.html**: added category creation

Collin Royal
- created checkout_all page that allows users to sumbit all their items in cart. 
- Also added promo code functionality allowing users to take some off of their final total. 
- added check availibility functionality that tells users if an item is available or not. If an item is not fully available the number is posted in red with a warning
- created way to submit full order in a users cart
- updated checkout order page to display availability
- created save for later functionality that allows users to move items in cart to separate section. 
- updated submit order funcitonality to decrease a buyer's bank account, increment a seller's account, and decrement a seller's inventory amount. 

Where to find my work
- **app/templates/cart.html** updated carts page in include submit all option aswell as a save for later functionality
- **app/templates/saved_for_later.html** created page to show a user which items are saved for later that allows user to move the items back to the cart
- **app/carts/py** updated submit order function and added functions to checkout all items in the cart. Also added functions for the save for later functionality
- **app/templates/checkout.html** added ability to see an items availability
- **app/templates/checkout_all** added checkout all page and implemented functions allowing user to submit a full order

