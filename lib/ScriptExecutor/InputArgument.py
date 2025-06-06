import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSignal

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(1, parentdir)

from UI.input_argument_options_ui import *

class Input_Argument(QWidget, Ui_Form):
    button_OK_clicked = pyqtSignal()

    def __init__(self, mainWindow):
        super(Input_Argument, self).__init__()
        self.setupUi(self)
        self.setWindowFlags( QtCore.Qt.WindowTitleHint |QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowStaysOnTopHint) 
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.mainWindow = mainWindow
        self.useDefault = True
        
        #self.pushButton_ok.clicked.connect(lambda: self.button_OK_clicked.emit())
        self.pushButton_ok.clicked.connect(self.changeStatus)
        self.pushButton_ok.clicked.connect(self.close)
    #end def

    def focusOutEvent(self,event):
        self.showNormal()

    def closeEvent(self, QCloseEvent):
        self.mainWindow.pushButton_Stop.setEnabled(True)
        QCloseEvent.accept()
    # end def

    def changeStatus(self):
        if self.radioButton_default.isChecked():
            self.useDefault = True
        else:
            self.useDefault = False
        self.button_OK_clicked.emit()
    #end def
#end class
