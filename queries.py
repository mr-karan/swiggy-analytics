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
get_total_orders_query = "SELECT count(order_id) from orders"
