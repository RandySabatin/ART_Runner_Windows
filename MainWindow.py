import sys
import os
import logging
import webbrowser
import threading
import multiprocessing
from multiprocessing import Process
import time
import zipfile
import yaml
import re
import copy

parentdir = (os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(1, parentdir)
bundle_dir = getattr(sys, '_MEIPASS', parentdir)

from Utils.tmlog import TmLog
from Utils.fileUtils import FileUtils

### for external scripts ###
import re
import atomic_operator
import platform


from Utils.systemUtils import SystemUtils
from Utils.processUtils import ProcessUtils
#############################


if (os.path.exists(os.getcwd() + r'/logs')) == False:
    os.makedirs('logs')
formatter="%(asctime)s [%(levelname)s]\t [%(process)x:%(thread)x][%(funcName)s]   - %(message)s - [%(filename)s(%(lineno)d)]"
TmLog.setup_logger('ART_Runner', "logs/ART_Runner.log", logging.INFO, formatter = formatter)
logger = TmLog.getLogger("ART_Runner")
logger.info("-------------------------------------Start-------------------------------------")

if getattr(sys, 'frozen', False):
    pro = FileUtils.getFileProperties(sys.executable)
    logger.info("ART_Runner Version: %s" %(str(pro["FileVersion"])))

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QDesktopWidget, QFileDialog
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QTextCursor

    from UI.icons import * #resource lib that contains icon
    import UI.perimeter_ui as PERIMETER_UI

    from lib.ScriptExecutor.InputArgument import Input_Argument
    from ExternalScripts.AtomicRedTeam.UserDefined import UserDefined
    
    
except Exception as err:
    logger.info(str(err))


class ToolWindow(PERIMETER_UI.Ui_SAHCMainWindow, QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self) # setup the main window UI from perimeter.py, 'self' become the mainwindow

        self.resultQueue = multiprocessing.Queue()
        self.QueueFromParent = multiprocessing.Queue()
        self.QueueFromChild = multiprocessing.Queue()
        self.eventParentSent = multiprocessing.Event()
        self.eventChildSent = multiprocessing.Event()
        self.eventChildSentFinish = multiprocessing.Event()

        self.Input_Argument = Input_Argument(self)

        self.isForceStop = False


    def setupUI(self):  # Entry point of the whole class
        self.setupPerimeter()
        
        #################
        self.process = None
        self.isProcessOn = False
        self.time2Check = 0

        self.Timer = QTimer(self)
        self.Timer.timeout.connect(self.RTMonitor)

        self.textBrowser_ExecutionStatus.setOpenExternalLinks(True)
        self.textBrowser_ExecutionDetails.setOpenExternalLinks(True)
        self.textBrowser_ScenarioDetails.setOpenExternalLinks(True)

        self.cursor_ExecutionStatus = QTextCursor(self.textBrowser_ExecutionStatus.document())
        self.cursor_ExecutionDetails = QTextCursor(self.textBrowser_ExecutionDetails.document())
        self.cursor_ScenarioDetails = QTextCursor(self.textBrowser_ScenarioDetails.document())

        self.SetScenarios()

        self.pushButton_Start.clicked.connect(self.StartExecution)
        self.pushButton_Stop.clicked.connect(self.StopExecution)
        self.pushButton_Path.clicked.connect(self.SetPath)

        self.Input_Argument.button_OK_clicked.connect(self.sendInputArgumentOption)

        self.setPowershellExecutionPolicy("Unrestricted")

        logger.info('UI is now ready!')
        ####################

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
    
    def setupPerimeter(self):
        perimeter_width = 980
        perimeter_height = 720
        self.setObjectName("BAS Demo")
        self.setGeometry(QtCore.QRect(200, 200, perimeter_width, perimeter_height))
        self.center()
    
    def closeEvent(self, QCloseEvent):
        if self.process:
            self.process.terminate()
        QCloseEvent.accept()
        sys.exit(0)

    # end def

    def resetUI(self):
        try:

            self.lineEdit_Path.setEnabled(False)
            self.pushButton_Path.setEnabled(False)
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(False)

            self.lineEdit_Path.setEnabled(True)
            self.pushButton_Path.setEnabled(True)

            UserPath = (self.lineEdit_Path.text()).strip()
            if len(UserPath):
                self.pushButton_Start.setEnabled(True)

        except Exception as err:
            logger.exception(str(err))

    def executingUI(self):
        try:


            self.lineEdit_Path.setEnabled(False)
            self.pushButton_Path.setEnabled(False)
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(True)

        except Exception as err:
            logger.exception(str(err))

    def DisableMainUI(self):
        try:
            self.lineEdit_Path.setEnabled(False)
            self.pushButton_Path.setEnabled(False)
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(False)

        except Exception as err:
            logger.exception(str(err))

    def SetScenarios(self):
        try:
            self.pushButton_Start.setEnabled(False)
            self.pushButton_Stop.setEnabled(False)


            self.lineEdit_Path.setEnabled(False)
            self.pushButton_Path.setEnabled(True)
            self.pushButton_Stop.setEnabled(False)
            return
        except Exception as e:
            logger.error("SetScenarios - " + str(e))
            return
    # end def

    def showMessageBox(self,message):
        try:
            self.msgboxClose = QtWidgets.QMessageBox()
            self.msgboxClose.setIcon(QtWidgets.QMessageBox.Question)
            self.msgboxClose.setWindowTitle("Atomic Red Team Runner")
            self.msgboxClose.setText(message)
            self.msgboxClose.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No);
            self.msgboxClose.setDefaultButton(QtWidgets.QMessageBox.No);
            answer = self.msgboxClose.exec();

            if answer == QtWidgets.QMessageBox.Yes:
                return "Yes"
            elif answer == QtWidgets.QMessageBox.No:
                return "No"
            else:
                return "Cancel"
        except Exception as err:
            logger.exception(str(err))
            return "Cancel"
    # end def

    def getTextInput(self, message, _defaultValue):
        try:
            _Value, _Done = QtWidgets.QInputDialog.getText(self, 'Scenario Needed Parameters', message, QtWidgets.QLineEdit.Normal, _defaultValue)

            if _Done:
                if len(_Value.strip()) <= 0:
                    return _defaultValue.strip()
                else:
                    return str(_Value).strip()
            else:
                return _defaultValue.strip()

        except Exception as err:
            logger.exception(str(err))
            return _defaultValue.strip()
    # end def

    def getPath(self,message):
        try:
            dir_str = ""
            dir_str = QFileDialog.getExistingDirectory(None, message, None, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if len(dir_str):
                dir_str = dir_str.replace('/', '\\')
            return dir_str
        except Exception as err:
            logger.exception(str(err))
            return ""
    # end def

    def getOption(self):
        try:
            self.pushButton_Stop.setEnabled(False)
            self.Input_Argument.show()
        except Exception as err:
            logger.exception(str(err))
            return True
    # end def

    def sendInputArgumentOption(self):
        try:
            self.QueueFromParent.put(self.Input_Argument.useDefault)
            self.eventParentSent.set()
        except Exception as err:
            logger.exception(str(err))
            return True
    # end def

    def RTMonitor(self):
        try:
            while not self.resultQueue.empty():
                result = self.resultQueue.get()

                if "{'function': '__" in result:

                    result2Dict = eval(result)
                    
                    if "__displayToExecutionStatus()" in result2Dict["function"]:
                        res = result2Dict["message"]
                        self.append_ExecutionStatus("%s" %res)

                    elif "__displayToExecutionDetails()" in result2Dict["function"]:
                        res = result2Dict["message"]
                        self.append_ExecutionDetails("%s" %res)

                    elif "__displayToScenarioDetails()" in result2Dict["function"]:
                        res = result2Dict["message"]
                        self.append_ScenarioDetails("%s" %res)

                    else:
                        res = result2Dict["message"]
                        self.append_ExecutionStatus("%s" %res)

                else:
                    res = result.strip()

                    if str(res).find('</font>') >= 0:
                        self.append_ExecutionStatus("%s" %res)
                    else:
                        self.append_ExecutionStatus("<font color=%s>%s</font>" % ('black', res))

            if (self.eventChildSent.is_set()) and (not self.QueueFromChild.empty()):
                msg = self.QueueFromChild.get()
                self.eventChildSent.clear()
                msg2Dict = eval(msg)

                if "__askConfirmation()" in msg2Dict["function"]:
                    res = self.showMessageBox(msg2Dict["message"])
                    self.QueueFromParent.put(res)
                    self.eventParentSent.set()
                elif "__getTextInput()" in msg2Dict["function"]:
                    res = self.getTextInput(msg2Dict["message"], msg2Dict["default_value"])
                    self.QueueFromParent.put(res)
                    self.eventParentSent.set()
                elif "__askPath()" in msg2Dict["function"]:
                    res = self.getPath(msg2Dict["message"])
                    self.QueueFromParent.put(res)
                    self.eventParentSent.set()
                elif "__askInputArgumentOption()" in msg2Dict["function"]:
                    self.getOption()


            #check every 6 seconds if the spawned process to run the scenario was terminated by others
            if (self.time2Check) and (time.time() - self.time2Check > 5):
                self.time2Check = time.time()
                current_PIDs = ProcessUtils.getAllProcessesToValues()

                if (self.isProcessOn) and (not self.eventChildSentFinish.is_set()) and (not self.eventChildSent.is_set()) and (self.process.pid not in current_PIDs) and (self.resultQueue.empty()):
                    self.append_ExecutionStatus("<font color=%s>%s</font>" % ('red', "Scenario execution was terminated. Please verify if your anti-virus is set to monitor-only mode."))
                    self.eventChildSentFinish.set()

            if (self.eventChildSentFinish.is_set()) and (self.resultQueue.empty()):
                self.eventChildSentFinish.clear()
                if self.isForceStop:
                    self.append_ExecutionStatus("<font color=%s>%s</font>" % ('green', "Scenario(s) execution is stopped."))
                else:
                    self.append_ExecutionStatus("<font color=%s>%s</font>" % ('green', "Finish Executing all the chosen scenario(s)."))
                
                self.process.join()
                self.isProcessOn = False
                self.resetUI()
                self.Timer.stop()
                self.time2Check = 0



        except Exception as err:
            logger.exception(str(err))

    def StopExecution(self):
        try:
            if (self.eventChildSent.is_set()):
                return

            if (self.eventChildSentFinish.is_set()):
                return
            self.pushButton_Stop.setEnabled(False)

            self.append_ExecutionStatus("<font color=%s size=+1>%s</font>" % ('green', "Stopping Scenario Execution ..."))

            self.process.terminate()
            self.eventChildSentFinish.set()

            self.resetUI()
            self.isForceStop = True

            return
        except Exception as e:
            logger.error("StopExecution - " + str(e))
            return
    # end def

    def StartExecution(self):
        try:
            self.executingUI()
            self.isForceStop = False

            self.clearQueue(self.resultQueue)
            self.clearQueue(self.QueueFromParent)
            self.clearQueue(self.QueueFromChild)
            self.eventParentSent.clear()
            self.eventChildSent.clear()
            self.eventChildSentFinish.clear()

            self.Timer.start(1000)

            self.TechniquePath = None

            self.TechniquePath = (self.lineEdit_Path.text()).strip()
            self.textBrowser_ExecutionStatus.clear()
            self.textBrowser_ExecutionDetails.clear()
            self.textBrowser_ScenarioDetails.clear()

            self.process = Process(target=executeScript, args=(self.resultQueue, \
                                                               self.QueueFromParent, self.QueueFromChild, \
                                                               self.eventParentSent, self.eventChildSent, \
                                                               self.eventChildSentFinish,  \
                                                               self.TechniquePath
                                                               ))

            self.process.start()
            self.isProcessOn = True
            self.time2Check = time.time()
        except Exception as e:
            logger.error("StartExecution - " + str(e))
    # end def

    def SetPath(self):
        try:
            dir_str = QFileDialog.getExistingDirectory(None, "Select the Atomic Red Team path", None, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if len(dir_str):
                dir_str = dir_str.replace('/', '\\')
                self.lineEdit_Path.setText(dir_str)
                self.lineEdit_Path.setEnabled(True)
                self.pushButton_Start.setEnabled(True)

        except Exception as err:
            logger.exception(str(err))

    def clearQueue(self, mpQueue):
        try:
            while not mpQueue.empty():
                mpQueue.get()
        except Exception as e:
            logger.error("clearQueue - " + str(e))
    #end def

    def append_ExecutionStatus(self, receivedText):
        try:
            receivedText = re.sub(r"black", "white", receivedText, flags=re.IGNORECASE)
            self.textBrowser_ExecutionStatus.moveCursor(QTextCursor.End)
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            self.cursor_ExecutionStatus.insertHtml("<font color=%s>%s</font>" % ('white', currentTime))
            self.cursor_ExecutionStatus.insertHtml(receivedText)
            self.cursor_ExecutionStatus.insertHtml("<br>")

            self.append_ExecutionDetails("%s" %receivedText)
        except Exception as e:
            logger.error("append_ExecutionStatus - " + str(e))
    #end def

    def append_ExecutionDetails(self, receivedText):
        try:
            receivedText = re.sub(r"black", "white", receivedText, flags=re.IGNORECASE)
            self.textBrowser_ExecutionDetails.moveCursor(QTextCursor.End)
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            self.cursor_ExecutionDetails.insertHtml("<font color=%s>%s</font>" % ('white', currentTime))
            self.cursor_ExecutionDetails.insertHtml(receivedText)
            self.cursor_ExecutionDetails.insertHtml("<br>")
        except Exception as e:
            logger.error("append_ExecutionDetails - " + str(e))
    #end def

    def append_ExecutionStatusNoTime(self, receivedText):
        try:
            receivedText = re.sub(r"black", "white", receivedText, flags=re.IGNORECASE)
            self.textBrowser_ExecutionStatus.moveCursor(QTextCursor.End)
            self.cursor_ExecutionStatus.insertHtml(receivedText)
            self.cursor_ExecutionStatus.insertHtml("<br>")

            self.append_ExecutionDetailsNoTime("%s" %receivedText)
        except Exception as e:
            logger.error("append_ExecutionStatus - " + str(e))
    #end def

    def append_ExecutionDetailsNoTime(self, receivedText):
        try:
            receivedText = re.sub(r"black", "white", receivedText, flags=re.IGNORECASE)
            self.textBrowser_ExecutionDetails.moveCursor(QTextCursor.End)
            self.cursor_ExecutionDetails.insertHtml(receivedText)
            self.cursor_ExecutionDetails.insertHtml("<br>")
        except Exception as e:
            logger.error("append_ExecutionDetails - " + str(e))
    #end def

    def append_ScenarioDetails(self, receivedText):
        try:
            receivedText = re.sub(r"black", "white", receivedText, flags=re.IGNORECASE)
            self.textBrowser_ScenarioDetails.moveCursor(QTextCursor.End)
            self.cursor_ScenarioDetails.insertHtml(receivedText)
            self.cursor_ScenarioDetails.insertHtml("<br>")
        except Exception as e:
            logger.error("append_ScenarioDetails - " + str(e))
    #end def

    def createFolder(self, folder="AtomicLauncher_Log"):
        try:
            "create folder[folder]"
            if os.path.exists(folder):
                logger.info("%s path has existed" %folder)
            else:
                os.makedirs(folder)
            #end if
        except Exception as err:
            logger.exception(str(err))
    
    #end def   

    def setHostSettings(self):
        try:
            self.msgboxClose = QtWidgets.QMessageBox()
            self.msgboxClose.setIcon(QtWidgets.QMessageBox.Question)
            self.msgboxClose.setWindowTitle("Atomic Red Team")
            saveMessage = ""
            saveMessage = saveMessage + 'Powershell execution policy must be set to "Unrestricted".'
            self.msgboxClose.setText(saveMessage)
            infoMessage = 'Do you allow this program to check and set the Powershell execution policy to "Unrestricted"?\n'
            infoMessage = infoMessage + "Click YES to proceed else click NO to end the program."
            self.msgboxClose.setInformativeText(infoMessage);
            self.msgboxClose.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No);
            self.msgboxClose.setDefaultButton(QtWidgets.QMessageBox.Yes);
            relay1 = self.msgboxClose.exec();

            if (relay1 == QtWidgets.QMessageBox.No):
                self.close()

            saveMessage = ""
            saveMessage = saveMessage + 'Tool will test the anti-malware setting.'
            self.msgboxClose.setText(saveMessage)
            infoMessage = 'EICAR test virus will be write/read on the system to verify the setting of your Endpoint Protection.\n'
            infoMessage = infoMessage + "Click YES to proceed else click NO to bypass EICAR test virus."
            self.msgboxClose.setInformativeText(infoMessage);
            self.msgboxClose.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No);
            self.msgboxClose.setDefaultButton(QtWidgets.QMessageBox.Yes);
            relay2 = self.msgboxClose.exec();

        except Exception as err:
            logger.exception(str(err)) 

    def setPowershellExecutionPolicy(self, setting):
        try:
            powershellPath = SystemUtils.getExecutablePath("powershell.exe")
            strExecCmd = powershellPath + r' Set-ExecutionPolicy ' + setting + ' -Force'
            result = SystemUtils.runCmdReturnOutput(strExecCmd)   
        except Exception as err:
            logger.exception(str(err))
    
    def getPowershellExecutionPolicy(self):
        try:
            powershellPath = SystemUtils.getExecutablePath("powershell.exe")
            strExecCmd = powershellPath + r' Get-ExecutionPolicy'
            result = SystemUtils.runCmdReturnOutput(strExecCmd)
            return result[0].strip()
        except Exception as err:
            logger.exception(str(err))
            return ""

def executeScript(resultQueue, \
                  QueueFromParent, QueueFromChild, \
                  eventParentSent, eventChildSent, \
                  eventChildSentFinish,  \
                  _techniquePath = None):
    try:

        Scenario = UserDefined()
        logger.info("Starts Executing [%s]. " %(_techniquePath))

        Scenario.setup__Case(resultQueue, QueueFromParent, QueueFromChild, \
                         eventParentSent, eventChildSent)

        Scenario.run(_techniquePath)
        
        resultQueue.put("Done executing [%s]." %(_techniquePath))
        logger.info("Done Executing [%s]. " %(_techniquePath))
        del Scenario

        eventChildSentFinish.set()
        return            
    except Exception as err:
        logger.exception(str(err))    