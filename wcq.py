import sys
import random
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

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


    
class WCQ(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(450,900)
       
        
        self.legend = get_legend()
        self.countries = list(self.legend.keys())
        self.countries_remaining = list(self.legend.keys())

        self.remaining_label = qtw.QLabel()
        self.remaining_label.setFont(qtg.QFont('Arial', 12))
        self.display_remaining()
        
        self.country_label = qtw.QLabel()
        self.country_label.setFont(qtg.QFont('Arial Black', 16))
        self.get_new_country()
        self.line_input = qtw.QLineEdit()
        self.line_input.returnPressed.connect(self.handle_input)

        
        self.table = qtw.QTableWidget(len(self.countries), 2)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1,150)
        
        self.table.setHorizontalHeaderLabels(['Country', 'Capital'])
        self.table.setVerticalHeaderLabels(['' for x in self.countries])
        for i, country in enumerate(self.countries):
            self.table.setItem(i, 0, qtw.QTableWidgetItem(country))

            
 
        
        
        
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
            row_index = self.countries.index(country)
            capital = self.legend[country][0]
            self.table.setItem(row_index, 1, qtw.QTableWidgetItem(capital))
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
        
    def win(self):
        self.country_label.setText('YOU WIN!')
        self.line_input.disconnect()
        self.line_input.returnPressed.connect(self.line_input.clear)
        

        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    wcq = WCQ(windowTitle='World Capitals Quiz')
    
    
    sys.exit(app.exec_())