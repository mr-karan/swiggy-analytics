import sqlite3
conn = sqlite3.connect('swiggy.db')


def init_db():
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INT UNIQUE, order_total FLOAT, restaurant_name VARCHAR, order_time DATETIME)")
    conn.commit()
    return None


def insert_orders(orders):
    cur = conn.cursor()
    cur.executemany(
        'INSERT INTO orders(order_id, order_total, restaurant_name, order_time) VALUES (?,?,?,?)', orders)
    conn.commit()
    return None
