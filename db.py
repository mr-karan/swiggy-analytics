import sqlite3
from exceptions import SwiggyDBError

from queries import create_table_query, insert_orders_query


class SwiggyDB(object):
    def init_db(self, persist=False):
        try:
            if persist:
                self.conn = sqlite3.connect('swiggy.db')
            else:
                self.conn = sqlite3.connect(':memory:')
        except Exception:
            raise SwiggyCliDBException("Unable to connect to DB")

    def create_db(self):
        cur = self.conn.cursor()
        cur.execute(create_table_query)
        self.conn.commit()

    def insert_orders(self, orders):
        cur = self.conn.cursor()
        # CAVEAT: Since this is a batch insert, even if one of the order already exists, the whole
        # transaction will fail and result in not adding the other unique orders
        # This is by design. Will think of a better way to handle later, it is not a huge issue now.
        try:
            cur.executemany(insert_orders_query, orders)
            self.conn.commit()
        except sqlite3.Error as e:
            if "UNIQUE" in "{}".format(e):
                pass
            else:
                raise SwiggyDBError("Error while inserting orders %s", e)
        except Exception as e:
            raise SwiggyDBError("Error while executing query %s", e)
