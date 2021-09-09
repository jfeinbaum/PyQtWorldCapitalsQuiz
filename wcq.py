import sys
import sqlite3
import random
from time import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


class WCQ(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(450,900)

        self.db = DB()
        self.countries = self.db.countries()

        self.countries_remaining = self.countries[:]
        
        self.start_time = 0

        self.stats_layout = qtw.QHBoxLayout()

        self.remaining_label = qtw.QLabel()
        self.remaining_label.setFont(qtg.QFont('Arial', 12))
        self.display_remaining()
        self.stats_layout.addWidget(self.remaining_label)

        self.n_skips_label = qtw.QLabel()
        self.n_skips_label.setFont(qtg.QFont('Arial', 12))
        
        self.country_label = qtw.QLabel()
        self.country_label.setFont(qtg.QFont('Arial Black', 16))
        self.get_new_country()

        self.skip_button = qtw.QPushButton('Skip')
        self.skip_button.setFixedWidth(50)
        self.skip_button.clicked.connect(self.skip)
        self.skips_used = 0

        self.give_up_button = qtw.QPushButton('Give Up')
        self.give_up_button.setFixedWidth(80)
        self.give_up_button.clicked.connect(self.give_up)

        self.play_again_button = qtw.QPushButton('Play Again')
        self.play_again_button.setFixedWidth(90)
        self.play_again_button.clicked.connect(self.play_again)

        # self.temp_win_button = qtw.QPushButton('Win (TEMP)')
        # self.temp_win_button.setFixedWidth(100)
        # self.temp_win_button.clicked.connect(self.win)

        self.line_input = qtw.QLineEdit()
        self.line_input.setFont(qtg.QFont('Arial',12))
        self.line_input.textChanged.connect(self.handle_input)

        
        self.table = qtw.QTableWidget(len(self.countries), 2)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1,150)
        
        self.table.setHorizontalHeaderLabels(['Country', 'Capital'])
        self.table.setVerticalHeaderLabels(['' for x in self.countries])
        for i, country in enumerate(self.countries):
            country_cell = qtw.QTableWidgetItem(country)
            country_cell.setFlags(country_cell.flags() & ~qtc.Qt.ItemIsEditable)
            country_cell.setFlags(country_cell.flags() & ~qtc.Qt.ItemIsSelectable)
            self.table.setItem(i, 0, country_cell)

            
 
        
        self.interactive_layout = qtw.QHBoxLayout()
        self.interactive_layout.addWidget(self.country_label)
        #self.interactive_layout.addWidget(self.temp_win_button)
        self.interactive_layout.addWidget(self.skip_button)
        self.interactive_layout.addWidget(self.give_up_button)
        
        layout = qtw.QVBoxLayout()
        layout.addLayout(self.stats_layout)
        layout.addLayout(self.interactive_layout)
        layout.addWidget(self.line_input)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.show()
    

    def handle_input(self):

        guess = self.line_input.text().lower()
        country = self.country_label.text()

        allowed_capitals = self.db.allowed_capitals_from_country(country)
        if guess in [cap.lower() for cap in allowed_capitals]:
        
            elapsed_time = time() - self.start_time
            old_time = self.db.get_country_time(country)
            new_time = (old_time + elapsed_time) / 2
            self.db.update_country_time(country, new_time)

            
            row_index = self.countries.index(country)
            capital = self.db.capital_from_country(country)
            capital_cell = qtw.QTableWidgetItem(capital)
            capital_cell.setFlags(capital_cell.flags() & ~qtc.Qt.ItemIsEditable)
            capital_cell.setFlags(capital_cell.flags() & ~qtc.Qt.ItemIsSelectable)
            self.table.setItem(row_index, 1, capital_cell)
            self.countries_remaining.remove(country)
            
            

            
            
            self.line_input.clear()
            self.display_remaining()
            if len(self.countries_remaining) == 0:
                self.win()
            else:
                self.get_new_country()
        
    def display_remaining(self):
        total = len(self.countries)
        remaining = len(self.countries_remaining)
        guessed = total - remaining
        self.remaining_label.setText(str(guessed) + '/' + str(total))
    
    def skip(self):
        self.skips_used += 1
        self.get_new_country()

    def get_new_country(self):
        country = random.choice(self.countries_remaining)
        self.country_label.setText(country)
        self.start_time = time()

    def end_game(self):
        self.line_input.disconnect()
        self.db.disconnect()
        self.give_up_button.close()
        self.skip_button.close()
        #self.temp_win_button.close()
        self.interactive_layout.addWidget(self.play_again_button)
        self.n_skips_label.setText('Skips used: ' + str(self.skips_used))
        self.stats_layout.addWidget(self.n_skips_label)

    def play_again(self):
        self.close()
        self.__init__()
        
    def win(self):
        self.country_label.setText('You Win!')
        self.end_game()

    def give_up(self):
        self.country_label.setText('Game Over')
        for row_index, country in enumerate(self.countries):
            capital = self.db.capital_from_country(country)
            capital_cell = qtw.QTableWidgetItem(capital)
            capital_cell.setFlags(capital_cell.flags() & ~qtc.Qt.ItemIsEditable)
            capital_cell.setFlags(capital_cell.flags() & ~qtc.Qt.ItemIsSelectable)
            self.table.setItem(row_index, 1, capital_cell)
        self.end_game()


        

        
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()

    def disconnect(self):
        self.conn.close()

    def capital_from_country(self, country):
        sql = ''' SELECT display_capital FROM data WHERE country=? '''
        self.cur.execute(sql, (country,))
        return self.cur.fetchall()[0][0]

    def countries(self):
        sql = ''' SELECT country FROM data ORDER BY country '''
        self.cur.execute(sql)
        return [r[0] for r in self.cur.fetchall()]

    def allowed_capitals_from_country(self, country):
        display_capital = self.capital_from_country(country)
        capitals = [display_capital]
        sql = ''' SELECT c.capital FROM allowed_capitals c 
        JOIN data d on d.id=c.country_id WHERE d.country=? '''
        self.cur.execute(sql, (country,))
        capitals.extend([r[0] for r in self.cur.fetchall()])
        return capitals

    def get_country_time(self, country):
        sql = ''' SELECT time FROM data where country=? '''
        self.cur.execute(sql, (country,))
        return self.cur.fetchall()[0][0]

    def update_country_time(self, country, time):
        sql = ''' UPDATE data SET time=? WHERE country=? '''
        self.cur.execute(sql, (time, country))



if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    wcq = WCQ(windowTitle='World Capitals Quiz')
    
    
    sys.exit(app.exec_())