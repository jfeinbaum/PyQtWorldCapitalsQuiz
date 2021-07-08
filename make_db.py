import sqlite3
from wcq import load_data



def main():

    data = load_data()

    conn = sqlite3.connect('data.db')
    cur = conn.cursor()



    cur.execute(''' CREATE TABLE IF NOT EXISTS data (country TEXT, display_capital TEXT, time DOUBLE); ''')

    for country, info in data.items():
        display_capital = info['display']
        time = info['time']
        cur.execute(''' INSERT INTO data VALUES (?, ?, ?) ''', (country, display_capital, time))

    conn.commit()
    conn.close()




if __name__ == '__main__':
    main()