import sys
import os
import json
import random
from time import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

'''
https://gis.stackexchange.com/questions/129959/problem-with-import-qgis-core-when-writing-a-stand-alone-pyqgis-script/130102#130102
'''
#from qgis.core import *


def load_data():
    with open('data.json', 'r') as fp:
        data = json.load(fp)
    return data

def save_data(data):
    json_str = json.dumps(data, indent=4)
    with open("data.json", "w") as fp:
        fp.write(json_str)

    
class WCQ(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(450,900)
       
        self.data = load_data()
        self.countries = list(self.data.keys())
        self.countries_remaining = list(self.data.keys())
        
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

        if guess in [cap.lower() for cap in self.data[country]["allowed"]]:
        
            elapsed_time = time() - self.start_time
            self.data[country]["time"] = (self.data[country]["time"] + elapsed_time) / 2
            
            row_index = self.countries.index(country)
            capital = self.data[country]["display"]
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
        save_data(self.data)
        

        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    wcq = WCQ(windowTitle='World Capitals Quiz')
    
    
    sys.exit(app.exec_())