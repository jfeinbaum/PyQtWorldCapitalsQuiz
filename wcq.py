import sys
import random
from time import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

#from qgis.core import *

'''
Reads .txt file, returns a dictionary
Each country maps to a list of acceptable capital names
legend[country][0] is the displayed capital
legend[country][1:] are the alternate spellings
'''
def get_legend():
    legend = {}
    fp = open('countriescapitals.txt', 'r')
    for line in fp.readlines():
        country, capitals = line.split(': ')
        legend[country] = capitals.strip('\n').split('; ')
    fp.close()
    return legend


def get_times():
    times = {}
    fp = open('countrytimes.txt', 'r')
    for line in fp.readlines():
        country, time_str = line.split(': ')
        time = float(time_str.strip('\n'))
        times[country] = time
    fp.close()
    return times
    
def save_times(times):
    fp = open('countrytimes.txt', 'w')
    for country, time in times.items():
        fp.write(country + ': '+ str(time) +'\n')
    fp.close()
    
class WCQ(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(450,900)
       
        
        self.legend = get_legend()
        self.countries = list(self.legend.keys())
        self.countries_remaining = list(self.legend.keys())
        
        self.times = get_times()
        self.start_time = 0

        self.remaining_label = qtw.QLabel()
        self.remaining_label.setFont(qtg.QFont('Arial', 12))
        self.display_remaining()
        
        self.country_label = qtw.QLabel()
        self.country_label.setFont(qtg.QFont('Arial Black', 16))
        self.get_new_country()
        self.line_input = qtw.QLineEdit()
        self.line_input.setFont(qtg.QFont('Arial',12))
        self.line_input.returnPressed.connect(self.handle_input)

        
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

            
 
        
        
        
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.remaining_label)
        layout.addWidget(self.country_label)
        layout.addWidget(self.line_input)
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.show()
    

    def handle_input(self):

        guess = self.line_input.text().lower()
        country = self.country_label.text()

        if guess in [cap.lower() for cap in self.legend[country]]:
        
            elapsed_time = time() - self.start_time
            if self.times[country] == 0:
                self.times[country] = elapsed_time
            else:
                self.times[country] = (self.times[country] + elapsed_time) / 2
            
            row_index = self.countries.index(country)
            capital = self.legend[country][0]
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
        self.remaining_label.setText('Remaining: ' + str(len(self.countries_remaining)))
    

    def get_new_country(self):
        country = random.choice(self.countries_remaining)
        self.country_label.setText(country)
        self.start_time = time()
        
    def win(self):
        self.country_label.setText('YOU WIN!')
        self.line_input.disconnect()
        self.line_input.returnPressed.connect(self.line_input.clear)
        save_times(self.times)
        

        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    wcq = WCQ(windowTitle='World Capitals Quiz')
    
    
    sys.exit(app.exec_())