import sys, os
import multiprocessing

from PyQt5 import QtCore, QtWidgets

parentdir = (os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(1, parentdir)

from MainWindow import ToolWindow

if __name__ == "__main__":
    # support High DPI settings  
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)    # enable highdpi scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)   # use highdpi icons

    app = QtWidgets.QApplication(sys.argv)
    multiprocessing.freeze_support()    # to support multi-thread with pyinstaller
    ToolWindow = ToolWindow()
    ToolWindow.setupUI()
    ToolWindow.show()
    #ToolWindow.setHostSettings()
    sys.exit(app.exec_())