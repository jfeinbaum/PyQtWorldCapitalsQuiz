import sys
import sqlite3
import subprocess
import random
import os
from time import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from init_db import DB_NAME


class WCQ(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(550, 900)

        self.db = DB()
        self.countries = self.db.countries()

        self.countries_remaining = self.countries[:]
        self.current_elapsed_times = {}

        self.elapsed_time = 0
        self.paused_elapsed_time = 0
        self.pause_ts = None
        self.resume_ts = None

        self.stats_layout = qtw.QHBoxLayout()

        self.remaining_label = qtw.QLabel()
        self.remaining_label.setFont(qtg.QFont('Arial', 12))
        self.display_remaining()
        self.stats_layout.addWidget(self.remaining_label)

        self.n_skips_label = qtw.QLabel()
        self.n_skips_label.setFont(qtg.QFont('Arial', 10))
        self.best_time_label = qtw.QLabel()
        self.best_time_label.setFont(qtg.QFont('Arial', 10))
        self.worst_time_label = qtw.QLabel()
        self.worst_time_label.setFont(qtg.QFont('Arial', 10))

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

        self.toggle_pause_button = qtw.QPushButton()
        self.toggle_pause_button.setFixedWidth(40)
        pause_pm = qtw.QStyle.SP_MediaPause
        pause_icon = self.style().standardIcon(pause_pm)
        self.toggle_pause_button.setIcon(pause_icon)
        self.game_paused = False
        self.toggle_pause_button.clicked.connect(self.toggle_pause)

        self.line_input = qtw.QLineEdit()
        self.line_input.setFont(qtg.QFont('Arial', 12))
        self.line_input.textChanged.connect(self.handle_input)

        self.table = qtw.QTableWidget(len(self.countries), 4)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 75)


        self.table.setHorizontalHeaderLabels(['Country', 'Capital', 'Time', 'Avg. Time'])
        self.table.setVerticalHeaderLabels(['' for x in self.countries])
        for i, country in enumerate(self.countries):
            self.fill_cell(i, 0, country)

        self.interactive_layout = qtw.QHBoxLayout()
        self.interactive_layout.addWidget(self.country_label)
        self.interactive_layout.addWidget(self.toggle_pause_button)
        # self.interactive_layout.addWidget(self.temp_win_button)
        self.interactive_layout.addWidget(self.skip_button)
        self.interactive_layout.addWidget(self.give_up_button)

        layout = qtw.QVBoxLayout()
        layout.addLayout(self.stats_layout)
        layout.addLayout(self.interactive_layout)
        layout.addWidget(self.line_input)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.show()

    def fill_cell(self, row_index, col_index, value):
        cell = qtw.QTableWidgetItem(value)
        cell.setFlags(cell.flags() & ~qtc.Qt.ItemIsEditable)
        cell.setFlags(cell.flags() & ~qtc.Qt.ItemIsSelectable)
        self.table.setItem(row_index, col_index, cell)


    def handle_input(self):

        guess = self.line_input.text().lower()
        country = self.country_label.text()

        allowed_capitals = self.db.allowed_capitals_from_country(country)
        if guess in [cap.lower() for cap in allowed_capitals]:

            elapsed_time = time() - self.resume_ts
            self.elapsed_time += elapsed_time
            old_time = self.db.get_country_time(country)
            new_time = (old_time + self.elapsed_time) / 2
            self.db.update_country_time(country, new_time)

            row_index = self.countries.index(country)
            capital = self.db.capital_from_country(country)
            self.fill_cell(row_index, 1, capital)
            self.countries_remaining.remove(country)

            self.current_elapsed_times[capital] = self.elapsed_time
            self.fill_cell(row_index, 2, str(round(self.elapsed_time, 3)))


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
        self.elapsed_time = 0
        self.paused_elapsed_time = 0
        self.resume_ts = time()

    def toggle_pause(self):
        if not self.game_paused:
            self.pause_ts = time()
            time_while_resumed = self.pause_ts - self.resume_ts
            self.elapsed_time += time_while_resumed

            resume_pm = qtw.QStyle.SP_MediaPlay
            resume_icon = self.style().standardIcon(resume_pm)
            self.toggle_pause_button.setIcon(resume_icon)
            self.line_input.setEnabled(False)
            self.skip_button.setEnabled(False)
            self.game_paused = True
        else:
            self.resume_ts = time()

            pause_pm = qtw.QStyle.SP_MediaPause
            pause_icon = self.style().standardIcon(pause_pm)
            self.toggle_pause_button.setIcon(pause_icon)
            self.line_input.setEnabled(True)
            self.line_input.setFocus(qtc.Qt.MouseFocusReason)
            self.skip_button.setEnabled(True)
            self.game_paused = False

    def end_game(self):

        for row_index, country in enumerate(self.countries):
            avg_time = self.db.get_country_time(country)
            self.fill_cell(row_index, 3, str(round(avg_time, 3)))

        self.line_input.disconnect()
        self.db.disconnect()
        self.give_up_button.close()
        self.skip_button.close()
        self.toggle_pause_button.close()
        # self.temp_win_button.close()
        self.interactive_layout.addWidget(self.play_again_button)
        if self.skips_used > 0:
            self.n_skips_label.setText('Skips: ' + str(self.skips_used))

        if self.current_elapsed_times:
            sorted_elapsed_times = sorted(self.current_elapsed_times.items(),
                                          key=lambda kv: (kv[1], kv[0]))
            best_c, best_t = sorted_elapsed_times[0]
            worst_c, worst_t = sorted_elapsed_times[-1]
            self.best_time_label.setText('Best: ' + str(round(best_t, 3)) + ' (' + best_c + ')')
            self.worst_time_label.setText('Worst: ' + str(round(worst_t, 3)) + ' (' + worst_c + ')')

        self.stats_layout.addWidget(self.n_skips_label)
        self.stats_layout.addWidget(self.best_time_label)
        self.stats_layout.addWidget(self.worst_time_label)


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
        self.conn = sqlite3.connect(DB_NAME)
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

    def update_country_time(self, country, new_time):
        sql = ''' UPDATE data SET time=? WHERE country=? '''
        self.cur.execute(sql, (new_time, country))


if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        subprocess.call(['python3', 'init_db.py'])
    app = qtw.QApplication(sys.argv)
    wcq = WCQ(windowTitle='World Capitals Quiz')

    sys.exit(app.exec_())
