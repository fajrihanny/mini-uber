import sqlite3

def make_database(ride_id,customer,driver):
    conn = sqlite3.connect('./customerider.db')
    c = conn.cursor()
    c.execute("insert into customerrider (ride_id,customer_phone,driver_phone) values (?,?,?)",(ride_id,customer,driver))
    conn.commit()
    conn.close()
