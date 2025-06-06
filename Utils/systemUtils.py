# -*- coding: utf-8 -*-
import os
import sys
import subprocess
#import wmi
import pythoncom
import time

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(1, parentdir)

from Utils.tmlog import TmLog
logger = TmLog.getLogger("ART_Runner")

# static utils class
class SystemUtils(object):
    @staticmethod
    def callExecute(cmd):
        try:
            cmd = os.getcwd() + cmd
            cmd = cmd.replace('\\', '/')
            if os.access(cmd, os.F_OK) is not True:
                print("File {} is not exist.".format(cmd))
                return None
            if os.access(cmd, os.X_OK) is not True:
                print("File {} is not accessible to execute.".format(cmd))
                return None
            # si = subprocess.STARTUPINFO()
            # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # si.wShowWindow = subprocess.SW_HIDE
            print("Call cmd {}".format(cmd))
            # subprocess.call(cmd, startupinfo=si)
            handler = subprocess.Popen(cmd, shell=True)
            return handler
        except subprocess.CalledProcessError as exc:
            print("CalledProcessError exception. Cmd:{} return error code {}, the output is {}.".format(exc.cmd, exc.returncode, exc.output))
            return None
        except OSError as e:
            print("OSError exception. Error num is {}, str error is {}, filename is {}".format(e.errno, e.strerror, e.filename))
            return None
        except Exception as err:
            print(str(err))
            return None

    @staticmethod
    def process_exists(process_name):
        try:
            call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
            # use buildin check_output right away
            output = subprocess.check_output(call)
            # check in last line for process name
            last_line = output.decode().strip().split('\r\n')[-1]
            # because Fail message could be translated
            return last_line.lower().startswith(process_name.lower())
        except Exception as err:
            print(str(err))
            return False

    @staticmethod
    def checkProcessRunning(handler, processName = ""):
        try:
            if handler is None:
                return False
            # check whether process is closed
            elif subprocess.Popen.poll(handler) == 0:
                return False
            else:
                return True
        except Exception as err:
            print(str(err))
            return False

    @staticmethod
    def isWindows32():
        try:
            if os.path.exists(os.getenv("SystemDrive") + r"\Program Files (x86)"):
                return False
            else:
                return True
        except Exception as err:
            print(str(err))

    @staticmethod
    def getService(servicename):
        pythoncom.CoInitialize()
        c = wmi.WMI()
        for service in c.Win32_Service(Name=servicename):
            return service
        return None

    @staticmethod
    def runCmdReturnOutput(cmd):
        try:
            logger.info("Running command: %s"%cmd)
            proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL,universal_newlines=True)
            output, errors = proc.communicate()
            if errors != '':
                 logger.error("error: %s" %errors)
            return output, errors
        except Exception as e:
            logger.exception("Exception happens: %s" % str(e))
            return '', ''

    @staticmethod
    def printScreen(MessageToPrint, isPrintToScreen = False):
        try:
            if(isPrintToScreen):
                currentTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
                stringToPrint = currentTime + ": " + str(MessageToPrint)
                print(stringToPrint)
            return
        except Exception as e:
            logger.exception("printScreen(): %s" % str(e))
            return

    @staticmethod
    def printScreenV2(MessageToPrint):
        try:
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            stringToPrint = currentTime + ": " + str(MessageToPrint)
            
            if(GLOBAL_VAR.CMD_Mode):
                print(stringToPrint)

            GLOBAL_VAR.DSAGlobalLogList.append(stringToPrint)
            return
        except Exception as e:
            logger.exception("printScreen(): %s" % str(e))
            return

    @staticmethod
    def getExecutablePath(executableFile):
        try:
            system32 = os.path.join(os.environ['SystemRoot'], 'SysNative' if os.path.exists(os.getenv("SystemDrive") + r"\Program Files (x86)") else 'System32')
            Path = os.path.join(system32, 'where.exe') 

            strExecCmd = Path + " " + executableFile

            output = SystemUtils.runCmdReturnOutput(strExecCmd)

            if len(output[0]) < 1:
                return None
            
            value = output[0][0:output[0].index(executableFile) + len(executableFile)]

            if 'SysNative' in system32:
                value = value.replace("System32","SysNative")

            return value
        except Exception as e:
            logger.exception("getExecutablePath(): %s" % str(e))
            return None

