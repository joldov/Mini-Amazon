\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);


\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.categories_id_seq',
                         (SELECT MAX(id)+1 FROM categories),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);



\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.carts_id_seq',
                         (SELECT MAX(id)+1 FROM Carts),
                         false);

 \COPY Review_Of_Product FROM 'Review_Of_Product.csv' WITH DELIMITER ',' NULL '' CSV
 SELECT pg_catalog.setval('public.review_of_product_id_seq',
                         (SELECT MAX(id)+1 FROM Review_Of_Product), 
                         false);
                    
\COPY Review_Of_Seller FROM 'Review_Of_Seller.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.review_of_seller_id_seq',
                         (SELECT MAX(id)+1 FROM Review_Of_Seller), 
                         false);



-- \COPY User_Upvotes_Product_Review FROM 'User_Upvotes_Product_Review.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.user_upvotes_product_review_id_seq',
--                          (SELECT MAX(id)+1 FROM User_Upvotes_Product_Review), 
--                          false);