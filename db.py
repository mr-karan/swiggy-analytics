import sqlite3
from exceptions import SwiggyDBError


class SwiggyDB(object):
    def init_db(self):
        try:
            self.conn = sqlite3.connect('swiggy.db')
        except Exception:
            raise SwiggyCliDBException("Unable to connect to DB")

    def create_db(self):
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INT UNIQUE, order_total FLOAT, restaurant_name VARCHAR, order_time DATETIME)")
        self.conn.commit()

    def insert_orders(self, orders):
        cur = self.conn.cursor()
        try:
            cur.executemany(
                'INSERT INTO orders(order_id, order_total, restaurant_name, order_time) VALUES (?,?,?,?)', orders)
            self.conn.commit()
        # except Exception as e:
        #     raise SwiggyDBError("Error while inserting orders: %s", e)
        except sqlite3.Error as e:
            if "UNIQUE" in "{}".format(e):
                pass
            else:
                raise SwiggyDBError("Error while inserting orders %s", e)
        except Exception as e:
            raise SwiggyDBError("Error while executing query %s", e)
