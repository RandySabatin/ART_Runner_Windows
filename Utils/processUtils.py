# -*- coding: utf-8 -*-
import os, sys#, wmi
import psutil

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parentdir)

from Utils.fileUtils import FileUtils

from Utils.tmlog import TmLog
logger = TmLog.getLogger("ART_Runner")
import pythoncom

class ProcessUtils(object):
    @staticmethod
    def getAllProcesses():
        pIdDict={}
        pIds = psutil.pids()
        for pId in pIds:
            try:
                p = psutil.Process(pId)
            except psutil.NoSuchProcess as e:
                logger.error(str(e))
                continue
            pIdDict[p.name().lower()] = pId
        return pIdDict

    @staticmethod
    def getAllProcessesToValues():
        pIdDict={}
        pIds = psutil.pids()
        for pId in pIds:
            try:
                p = psutil.Process(pId)
                pIdDict[pId] = str(p.name()).lower()
            except:
                continue
        return pIdDict

    @staticmethod
    def checkProcess(processNode):
        try:
            pId = ProcessUtils.getProcessId(processNode.name.lower())
            if not pId:
                return None, ""
            processState = ProcessUtils.getProcessState(pId)
            if processState == "":
                return False, ""
            return (processState.lower() == processNode.state.lower()), processState
        except Exception as err:
            print(str(err))
            return False, ""

    @staticmethod
    def getProcessId(processName):
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            wql = 'SELECT * FROM Win32_Process WHERE Name = "{}"'.format(processName)
            process = c.query(wql)
            if not process:
                return None
            return process[0].Handle
        except Exception as err:
            print(str(err))
            print("Get driver {} error!".format(processName))
            return None

    @staticmethod
    def getProcessState(pId):
        try:
            p = psutil.Process(int(pId))
            return p.status()
        except Exception as err:
            print(str(err))
            return ""

    @staticmethod
    def processExits(processName, pIdDict):
        return processName.lower() in pIdDict

    @staticmethod
    def getProcessExePath(processName, pIdDict):
        if processName.lower() in pIdDict:
            p = psutil.Process(pIdDict[processName.lower()])
            try:
                return p.exe()
            except psutil.AccessDenied:
                logger.error("AccessDenied for getProcessExePath {}".format(processName))
                return ""
