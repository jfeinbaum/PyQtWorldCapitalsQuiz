import sqlite3
import os


def main():

    db_name = 'data.db'
    data = {}

    fp = open('countriescapitals.txt', 'r')
    for line in fp.readlines():
            country, capitals = line.split(': ')
            data[country] = {}
            capitals = capitals.split(';')
            data[country]['display'] = capitals[0]
            data[country]['allowed'] = capitals


    fp.close()

    if os.path.exists(db_name):
        remake = input('Are you sure you want to remake the database? Metadata will be lost!\nY or N: ').lower()
        if remake == 'n':
            print('Okay, keeping original', db_name)
            return


    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute(''' DROP TABLE IF EXISTS data; ''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS data 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, display_capital TEXT, time DOUBLE); ''')

    cur.execute(''' DROP TABLE IF EXISTS allowed_capitals;''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS allowed_capitals
     (country_id INTEGER, capital TEXT, FOREIGN KEY (country_id) REFERENCES data (id) ); ''')

    for country, info in data.items():
        display_capital = info['display']
        cur.execute(''' INSERT INTO data (country, display_capital, time) VALUES (?, ?, ?);''', (country, display_capital, 0))
        id = cur.lastrowid
        allowed = info['allowed']
        for capital in allowed:
            if capital != display_capital:
                cur.execute(''' INSERT INTO allowed_capitals VALUES (?, ?); ''', (id, capital))

    conn.commit()
    conn.close()

    print('Created', db_name)

if __name__ == '__main__':
    main()