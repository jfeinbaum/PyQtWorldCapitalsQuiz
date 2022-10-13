import sqlite3
import os


DB_NAME = 'data.db'

def main():


    data = {}

    fp = open('countriescapitals.txt', 'r')
    for line in fp.readlines():
            country, capitals = line.split(': ')
            data[country] = {}
            capitals = [s.strip('\n') for s in capitals.split(';')]
            data[country]['display'] = capitals[0]
            data[country]['allowed'] = capitals


    fp.close()

    if os.path.exists(DB_NAME):
        while True:
            remake = input('Are you sure you want to remake the database? Metadata will be lost!\nY or N: ').lower()
            if remake == 'n':
                print('Okay, keeping original', DB_NAME)
                return
            elif remake == 'y':
                break


    conn = sqlite3.connect(DB_NAME)
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

    print('Created', DB_NAME)

if __name__ == '__main__':
    main()