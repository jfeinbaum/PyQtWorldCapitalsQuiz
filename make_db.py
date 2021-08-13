import sqlite3
import json
from wcq import load_data



def main():

    with open('data.json', 'r') as fp:
        data = json.load(fp)

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute(''' DROP TABLE IF EXISTS data; ''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS data 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, display_capital TEXT, time DOUBLE); ''')

    cur.execute(''' DROP TABLE IF EXISTS allowed_capitals;''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS allowed_capitals
     (country_id INTEGER, capital TEXT, FOREIGN KEY (country_id) REFERENCES data (id) ); ''')

    for country, info in data.items():
        display_capital = info['display']
        time = info['time']
        cur.execute(''' INSERT INTO data (country, display_capital, time) VALUES (?, ?, ?);''', (country, display_capital, time))
        id = cur.lastrowid
        allowed = info['allowed']
        for capital in allowed:
            if capital != display_capital:
                cur.execute(''' INSERT INTO allowed_capitals VALUES (?, ?); ''', (id, capital))

    conn.commit()
    conn.close()




if __name__ == '__main__':
    main()