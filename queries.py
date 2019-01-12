create_table_query = "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INT UNIQUE, order_total FLOAT, restaurant_name VARCHAR, order_time DATETIME)"
insert_orders_query = "INSERT INTO orders(order_id, order_total, restaurant_name, order_time) VALUES (?,?,?,?)"
