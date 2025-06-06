import sys
import os
import time

from Utils.tmlog import TmLog
logger = TmLog.getLogger("Atomic_Launcher")

class BaseCase:

    def __init__(self):
        try:
            self.name = "BaseCase Name"
            self.detail = "Detail: This is the basecase."
            self.time_out = 10 #minutes

            self.log__Queue =  None
            self.Queue__FromParent = None
            self.Queue__FromChild = None
            self.event__ParentSent = None
            self.event__ChildSent = None
            self.CMD__Mode = False
            self.need__ToFix = False

        except Exception as err:
            logger.exception(str(err))
    
    def __del__(self):
        pass

    def setup__Case (self, logQueue, QueueFromParent, QueueFromChild, eventParentSent, eventChildSent, CMD_Mode = False, needToFix = False):
        try:
            self.log__Queue =  logQueue
            self.Queue__FromParent = QueueFromParent
            self.Queue__FromChild = QueueFromChild
            self.event__ParentSent = eventParentSent
            self.event__ChildSent = eventChildSent

            self.CMD__Mode = CMD_Mode
            self.need__ToFix = needToFix

            #self.displayToExecutionStatus(self.detail)
        except Exception as e:
            logger.error(str(e))
            return

    def askConfirmation(self, message = ""):
        try:
            if(self.CMD__Mode):
                return self.need__ToFix

            Str2Dict = {}
            Str2Dict["function"] = "__askConfirmation()"
            Str2Dict["message"] = message.strip()

            self.Queue__FromChild.put(str(Str2Dict))
            self.event__ChildSent.set()

            self.event__ParentSent.wait()
            response = self.Queue__FromParent.get()
            self.event__ParentSent.clear()

            return response
        except Exception as e:
            logger.error(str(e))
            return False

    def getTextInput(self, message = "", defaultValue = ""):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__getTextInput()"
            Str2Dict["message"] = message.strip()
            Str2Dict["default_value"] = defaultValue.strip()

            self.Queue__FromChild.put(str(Str2Dict))
            self.event__ChildSent.set()

            self.event__ParentSent.wait()
            response = self.Queue__FromParent.get()
            self.event__ParentSent.clear()

            return response
        except Exception as e:
            logger.error(str(e))
            return False

    def askPath(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__askPath()"
            Str2Dict["message"] = message.strip()

            self.Queue__FromChild.put(str(Str2Dict))
            self.event__ChildSent.set()

            self.event__ParentSent.wait()
            response = self.Queue__FromParent.get()
            self.event__ParentSent.clear()

            return response
        except Exception as e:
            logger.error(str(e))
            return False

    def askInputArgumentOption(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__askInputArgumentOption()"
            Str2Dict["message"] = message.strip()

            self.Queue__FromChild.put(str(Str2Dict))
            self.event__ChildSent.set()

            self.event__ParentSent.wait()
            response = self.Queue__FromParent.get()
            self.event__ParentSent.clear()

            return response
        except Exception as e:
            logger.error(str(e))
            return False
    
    def displayMessage(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__displayToExecutionStatus()"
            Str2Dict["message"] = message.strip()

            self.log__Queue.put(str(Str2Dict))
        except Exception as e:
            logger.error(str(e))
            return


    def displayToExecutionStatus(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__displayToExecutionStatus()"
            Str2Dict["message"] = message.strip()

            self.log__Queue.put(str(Str2Dict))
        except Exception as e:
            logger.error(str(e))
            return

    def displayToExecutionDetails(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__displayToExecutionDetails()"
            Str2Dict["message"] = message.strip()

            self.log__Queue.put(str(Str2Dict))
        except Exception as e:
            logger.error(str(e))
            return

    def displayToV1Detections(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__displayToV1Detections()"
            Str2Dict["message"] = message.strip()

            self.log__Queue.put(str(Str2Dict))
        except Exception as e:
            logger.error(str(e))
            return

    def displayToScenarioDetails(self, message):
        try:
            Str2Dict = {}
            Str2Dict["function"] = "__displayToScenarioDetails()"
            Str2Dict["message"] = message.strip()

            self.log__Queue.put(str(Str2Dict))
        except Exception as e:
            logger.error(str(e))
            return