# create table queries
create_orders_table_query = """
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INT UNIQUE, order_total FLOAT, restaurant_name VARCHAR,
order_time DATETIME, rain_mode BOOLEAN, on_time BOOLEAN)
"""

create_items_table_query = """
CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INT,
name VARCHAR, is_veg BOOLEAN,
FOREIGN KEY(order_id) REFERENCES orders(order_id))
"""

# insert records queries
insert_orders_query = """
INSERT INTO orders(order_id, order_total, restaurant_name, order_time, rain_mode, on_time) VALUES (?,?,?,?,?,?)
"""
insert_items_query = """
INSERT INTO items(order_id, name, is_veg) VALUES (?,?,?)
"""

# analytics queries
get_total_orders_query = """
SELECT count(order_id) from orders
"""
get_total_amount_query = """
SELECT sum(order_total) from orders
"""
get_items_name_count_query = """
SELECT name, count(id) as ctr from items group by name order by ctr desc limit 10
"""
get_top_20_restaurants_query = """
SELECT "restaurant_name" AS "restaurant_name", count(*) AS "count"
FROM "orders"
GROUP BY "restaurant_name"
ORDER BY "count" DESC LIMIT 10
"""
get_order_count_day_of_week = """
SELECT CAST((strftime('%w', "order_time")) AS integer) AS "order_time", count(*) AS "count"
FROM "orders"
GROUP BY CAST((strftime('%w', "order_time")) AS integer)
ORDER BY CAST((strftime('%w', "order_time")) AS integer) ASC
"""
get_monthly_spend_count = """
SELECT date("order_time", 'start of month') AS "order_time", sum("order_total") AS "sum", count(*) AS "count"
FROM "orders"
GROUP BY date("order_time", 'start of month')
ORDER BY date("order_time", 'start of month') ASC
"""
