#Imports
import sys
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QPainter
#Import various QWidgets
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog, QDialog, QTextEdit)
from PySide2.QtCharts import QtCharts
#Import hack language definitions
from hackdefinitions import comp, dest, jump, symbols
import re
import gc

#Set global variables for filepaths
openpath = None
savepath = None
#Used to store output for saving file in MainWindow class
opfile   = []

#Widget Class
class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0

        # Initialise dictionaries
        self._data = {}
        self._comp = {}

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Instructions", "Compiled"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Set row select
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Disable editing
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Create text widget
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        # Init buttons side by side
        self.split = QHBoxLayout()
        self.split.setMargin(10)
        self.split.addWidget(self.text)
        self.split.addWidget(self.table)

        # Add Push Button
        self.compile = QPushButton("Compile")
        self.clear = QPushButton("Clear")

        # Set text box and table next to each other
        self.right = QHBoxLayout()
        self.right.setMargin(10)
        self.right.addWidget(self.compile)
        self.right.addWidget(self.clear)

        # QWidget vertical Layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.split)
        self.layout.addLayout(self.right)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # Setup signals and slots
        self.compile.clicked.connect(self.add_element)
        self.clear.clicked.connect(self.clear_table)

        # Fill table with empty data
        self.fill_table()

    @Slot()
    def add_element(self):

        # Empty table
        self.table.setRowCount(0)
        # Loop counter
        self.items = 0

        # Compiler method
        def compile(instruction):
            #Compile C-Instruction
            if "=" in instruction or ";" in instruction and not "@" in instruction:
                if "=" in instruction and not ";" in instruction:
                    des = instruction.split('=')
                    # Pad with null
                    des.insert(2,'null')
                    return("111" + comp.get(des[1]) + dest.get(des[0]) + jump.get(des[2]))
                elif "=" not in instruction and ";" in instruction:
                    des = instruction.split(';')
                    des.insert(0,'null')
                    return("111" + comp.get(des[1]) + dest.get(des[0]) + jump.get(des[2]))
                elif "=" in instruction and ";" in instruction:
                    des = re.split(';|=', instruction)
                    return("111" + comp.get(des[1]) + dest.get(des[0]) + jump.get(des[2]))
            #Compile A-Instruction
            elif instruction.startswith('@') and not ";" in instruction and not "=" in instruction:
                if instruction[1:].isdigit():
                    return(f"0{int(instruction[1:]):015b}")
                elif not instruction[1:].isdigit():
                    des = instruction[1:]
                if des in symbols:
                    return(f"0{int(symbols.get(des)):015b}")
                elif des in tempdict:
                    return(f"0{int(tempdict.get(des)):015b}")
            #Error message if the instruction doesn't match
            else:
                return("ERRROR!")

        #Open file and store in list
        with open(openpath) as f:
            test = f.read()
            assembly = test.splitlines()
        f.close()

        # Set text box to file contents
        self.text.setPlainText(test)

        #Format ASM File
        #Remove whitespace
        rmw = [x.strip(' ') for x in assembly]
        #Remove line comments
        rmw = [x for x in rmw if not x.startswith('/')]
        #Remove in-line comments
        rmw = [x.split(' ', 1)[0] for x in rmw]
        #Remove empty list entries
        rmw = [x.strip() for x in rmw if x.strip()]

        #Extract Custstom Labels & Variables
        #Add (xxx) labels to list
        labels        = [x.strip('()') for x in rmw if x.startswith('(')]
        labelindex    = [i for i, x in enumerate(rmw) if x.startswith('(')]
        labelindexadj = [x-labelindex.index(x) for x in labelindex]
        #Remove labels comments
        rmw = [x for x in rmw if not x.startswith('(')]
        #Add custom vars to list
        varssymb      = [x[1:] for x in rmw if x.startswith('@') and not x[1:].isdigit() and x[1:] not in symbols and x[1:] not in labels]
        #Above add all instances of vars, so this function places unique values into new list
        varsunique    = list(dict.fromkeys(varssymb))
        varsymbindex  = [i+16 for i, x in enumerate(varsunique)]

        #Combine var and symbol lists
        tablesym      = labels + varssymb
        tableval      = labelindexadj + varsymbindex
        #Zip lists together and put in dictionary
        zipbObj       = zip(tablesym, tableval)
        tempdict      = dict(zipbObj)

        #Compile ASM File
        Output        = [compile(x) for x in rmw]

        # Make aware of global variable
        global opfile
        opfile.clear()

        # File table with assembled data
        for x, y in zip(rmw, Output):
            self.table.insertRow(self.items)
            self.table.setItem(self.items, 0, QTableWidgetItem(x))
            self.table.setItem(self.items, 1, QTableWidgetItem(y))
            self.table.resizeRowsToContents()
            self.items += 1
            # Global list for file save
            opfile.append(y)
            print(self.items, y)
                
    # Fill table method
    def fill_table(self, data=None):
        data = self._data if not data else data
        for desc, price in data.items():
            description_item = QTableWidgetItem(desc)
            price_item = QTableWidgetItem("{:.2f}".format(price))
            price_item.setTextAlignment(Qt.AlignRight)
            self.table.insertRow(self.items)
            self.table.setItem(self.items, 0, description_item)
            self.table.setItem(self.items, 1, price_item)
            self.items += 1

    # Clears table and text box
    @Slot()
    def clear_table(self):
        self.text.setPlainText(None)
        self.table.setRowCount(0)
        self.items = 0


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        # Set initial window title
        self.setWindowTitle("Hack ASM Compiler")
        
        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.help_menu = self.menu.addMenu("Help")

        # Open QAction
        open_action = QAction("Open..", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        # Save QAction
        save_action = QAction("Save..", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        # About QAction
        about_action = QAction("About", self)
        about_action.triggered.connect(self.informationMessage)

        # Setup signals
        self.file_menu.addAction(open_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addSeparator()
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)
        self.help_menu.addAction(about_action)
        self.setCentralWidget(widget)

    # Exit program
    def exit_app(self, checked):
        QApplication.quit()

    # Setup 'about' pop-up
    def informationMessage(self):
        d = QDialog()
        d.setFixedSize(240, 120)
        d.setWindowTitle("About")
        d.setWindowModality(Qt.ApplicationModal)
        d.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        # Set body of pop-up windows
        d.label = QLabel("<html><head/><body><p align=\"center\">Hack ASM Compiler v0.1</p><p align=\"center\">Joseph Roddis</p><p align=\"center\">2020</p><p align=\"center\"><a href=\"github.com/SgtSiff/Nand-to-Tetris-Assembler\"><span style=\" text-decoration: underline; color:#0000ff;\">github.com/SgtSiff/Nand-to-Tetris-Assembler</span></a></p></body></html>", parent=d)
        d.label.setGeometry(QtCore.QRect(0, 0, 240, 120))
        font = QtGui.QFont()
        font.setKerning(True)
        d.label.setFont(font)
        d.label.setScaledContents(False)
        d.label.setAlignment(QtCore.Qt.AlignCenter)
        d.label.setObjectName("label")
        #d.setWindowIcon(QIcon(":/icons/kdevelop.png"))
        d.exec_()

    # Open file method
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","ASM (*.asm)", options=options)
        if fileName:
            global openpath
            # Store file path to global variable
            openpath = fileName
            # Parse filename and append to window title
            filesplit = openpath.rsplit('/',1)
            windowname = "Hack ASM Compiler"
            self.setWindowTitle(windowname+" - "+filesplit[1])
            print(openpath)

    # Save file method
    def save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Hack Files (*.hack)", options=options)
        if fileName:
            global savepath
            savepath = fileName
            # Fix extension to .hack
            # Write to file
            with open(savepath+'.hack', 'w') as f:
                for item in opfile:
                    f.write("%s\n" % item)


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
