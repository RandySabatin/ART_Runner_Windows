# -*- coding: utf-8 -*-
import sys
import os
import shutil
import zipfile
import win32api
import pefile

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(1, parentdir)

from Utils.tmlog import TmLog
logger = TmLog.getLogger("ART_Runner")

class FileUtils(object):
    @staticmethod
    # Return the line number of a file
    def getFileLineNumber(filePath):
        count = 0
        try:
            f = open(filePath, 'r', encoding='utf8', errors='ignore')
            for line in f:
                count += 1
            f.close()
            return count
        except Exception as err:
            logger.exception(str(err))
            return count

    @staticmethod
    def getFileExistence(filePath):
        return os.path.exists(filePath)

    @staticmethod
    # Return the file size (MB)
    def getFileSize(filePath):
        try:
            return os.path.getsize(filePath)/(1024*1024)
        except Exception as err:
            logger.exception(str(err))
            return None

    @staticmethod
    # Return the file size (Bytes)
    def getFileSizeinBytes(filePath):
        try:
            return os.path.getsize(filePath)
        except Exception as err:
            logger.info("Failed to get the size of " + filePath)
            return None

    @staticmethod
    # Create a folder in the path
    def createLogFolder(folderPath ,folderName):
        try:
            logPath = folderPath + '/' + folderName
            if not os.path.exists(logPath):
                os.mkdir(logPath)
        except Exception as err:
            logger.exception("Create file folder failed!")
            logger.exception(str(err))

    @staticmethod
    # Return all the files in the folder with file path list
    def getFilesInFolder(fileDir):
        filePaths = []
        try:
            for root, _, files in os.walk(fileDir):
                for file in files:
                    filePaths.append(os.path.join(root, file))
            return filePaths
        except Exception as err:
            logger.exception(str(err))
            return filePaths

    @staticmethod
    # Return file name without filetype, eg. file.txt -> file
    def removeFileType(fileName):
        try:
            return fileName.partition('.')[0]
        except Exception as err:
            logger.exception(str(err))
            return ""

    @staticmethod
    def getFileName(filePath):
        try:
            return os.path.basename(filePath)
        except Exception as err:
            logger.exception(str(err))
            return ""
    
    @staticmethod
    # Return the file type from file path
    def getFileType(filePath):
        try:
            return os.path.splitext(filePath)[-1]
        except Exception as err:
            logger.exception(str(err))
            return ""  

    @staticmethod
    # Return folder path from file path
    def getFolderPath(filePath):
        try:
            return os.path.dirname(filePath)
        except Exception as err:
            logger.exception(str(err))
            return ""  

    @staticmethod
    # Return signature of the file
    def getFileSignature(filePath):
        try:
            import win32com.client
            s = win32com.client.gencache.EnsureDispatch('capicom.signedcode', 0)
            s.FileName = filePath
            signer = s.Signer
            return signer.Certificate.SubjectName
        except Exception as err:
            logger.exception(str(err))
            return ""
    
    @staticmethod
    # return last modify time
    def getModifyTime(filePath):
        try:
            return os.path.getmtime(filePath)
        except Exception as err:
            print(str(err))
            import time
            return time.time()

    @staticmethod
    # Return True if file is a compressed files
    def isCompressedFile(filePath):
        try:
            compressedFileTypes = [".zip", ".7z", ".gz", ".tar", ".bz2"]
            for fileType in compressedFileTypes:
                if filePath.endswith(fileType):
                    return True
            return False
        except Exception as err:
            logger.exception(str(err))
            return False

    @staticmethod
    # Return True if file is a text file
    def isTextFile(filePath):
        try:
            textFileTypes = [".log", ".ini", ".reg", ".txt"]
            for fileType in textFileTypes:
                if filePath.endswith(fileType):
                    return True
            return False
        except Exception as err:
            logger.exception(str(err))
            return False

    @staticmethod
    # Delete the entire folder
    def deleteFolder(folderPath):
        try:
            shutil.rmtree(folderPath, ignore_errors=True)
        except Exception as err:
            logger.exception(str(err))    
            return

    @staticmethod
    # Delete the files
    def deleteFiles(filePaths):
        for file in filePaths:
            try:
                if file == "":
                    continue
                os.remove(file)
            except Exception as err:
                logger.exception(str(err))

    @staticmethod
    # detect if OS is Windows
    def isWindows():
        try:
            if os.path.exists(os.getenv("SystemDrive") + r"\Program Files"):
                return True
            else:
                return False
        except Exception as err:
             logger.exception(str(err))

    @staticmethod
    # RECURSIVE uncompressed the file
    # Note: Need delete the extract tmp folder after yara rule scan
    def uncompressedFile(filePath, extractPath):
        if FileUtils.isCompressedFile(filePath) is False:
            # print("This isn't compressed file!")
            return
        import subprocess
        if self.isWindows():
            exePath = os.path.join(parentdir, r"Tools\SevenZip\7za.exe")
        else:
            exePath = os.path.join(parentdir, r"Tools/SevenZip/linux/7zz")
        zipPwd = "sample"
        try:
            # if os.access(exePath, os.F_OK) is False:
            #     print("File {} is not exist.".format(exePath))
            #     return
            # 7z.exe x test.zip -oD:\test -aoa
            cmd = r'"{}"'.format(exePath) + " x " + r'"{}"'.format(filePath) + " -o" + r'"{}"'.format(extractPath) + " -p" + zipPwd + " -aoa"
            cmd = cmd.replace('\\', '/')
            print("Call cmd {}".format(cmd))
            # subprocess.call(cmd, startupinfo=si)
            handler = subprocess.Popen(cmd, shell=True)
            handler.wait()
        except subprocess.CalledProcessError as exc:
            logger.exception("CalledProcessError exception. Cmd:{} return error code {}, the output is {}.".format(exc.cmd, exc.returncode, exc.output))
            return
        except OSError as e:
            logger.exception("OSError exception. Error num is {}, str error is {}, filename is {}".format(e.errno, e.strerror, e.filename))
            return
        except Exception as err:
            logger.exception(str(err))    
            return
        FileUtils.recrusiveUncompressed(extractPath)

    @staticmethod
    # Uncompressed files in the folder
    def recrusiveUncompressed(folderPath):
        logger.exception("recrusiveUncompressed")
        try:
            filePaths = FileUtils.getFilesInFolder(folderPath)
            for filePath in filePaths:
                extractPath = FileUtils.getFolderPath(filePath) + '/tmpUnCompressed'
                FileUtils.uncompressedFile(filePath, extractPath)
        except Exception as err:
            print(str(err))    
            return

    @staticmethod
    # (NOT RECURSIVE) uncompressed the file
    def decompressFile(filePath, extractPath, user_passwd = ""):
        zipPwdList = ["novirus", "virus"]
        zipPwd = "test"

        if len(user_passwd):
            zipPwd = user_passwd
        else:
            zipPwd = "test"

        if FileUtils.isCompressedFile(filePath) is False:
            # print("This isn't compressed file!")
            return

        if not len(user_passwd):
            #Get the right password from the list
            zippedFile = zipfile.ZipFile(filePath)
            for zinfo in zippedFile.infolist():
                isEncrypted = zinfo.flag_bits & 0x1 
                if (isEncrypted):
                    for passwd in zipPwdList:
                        try:
                            zippedFile.setpassword(pwd = bytes(passwd, 'utf-8'))
                            zippedFile.extract(zinfo.filename, extractPath + '/temp_folder')
                            shutil.rmtree(extractPath + '/temp_folder')
                            zipPwd = passwd
                            break
                        except:
                            continue
                    break
                else:
                    break

        import subprocess
        exePath = os.path.join(parentdir, r"Tools\SevenZip\7za.exe")
        
        try:
            # 7z.exe x test.zip -oD:\test -aoa
            cmd = r'"{}"'.format(exePath) + " x " + r'"{}"'.format(filePath) + " -o" + r'"{}"'.format(extractPath) + " -p" + zipPwd + " -aoa"
            cmd = cmd.replace('\\', '/')
            print("Call cmd {}".format(cmd))
            # subprocess.call(cmd, startupinfo=si)
            handler = subprocess.Popen(cmd, shell=True)
            handler.wait()
        except subprocess.CalledProcessError as exc:
            logger.exception("CalledProcessError exception. Cmd:{} return error code {}, the output is {}.".format(exc.cmd, exc.returncode, exc.output))
            return
        except OSError as e:
            logger.exception("OSError exception. Error num is {}, str error is {}, filename is {}".format(e.errno, e.strerror, e.filename))
            return
        except Exception as err:
            logger.exception(str(err))    
            return

    @staticmethod
    # compress the path
    def compressPath(path2Compress, zipfilePath, passwd=None):
        import subprocess
        exePath = os.path.join(parentdir, r"Tools\SevenZip\7za.exe")
        
        try:
            if (passwd):
                zipPwd = passwd
                cmd = r'"{}"'.format(exePath) + " a " + r'"{}"'.format(zipfilePath) + " " + r'"{}"'.format(path2Compress) + " -p" + zipPwd + " -y"
            else:
                cmd = r'"{}"'.format(exePath) + " a " + r'"{}"'.format(zipfilePath) + " " + r'"{}"'.format(path2Compress) + " -y"
            cmd = cmd.replace('\\', '/')

            #print("Call cmd {}".format(cmd))
            # subprocess.call(cmd, startupinfo=si)
            handler = subprocess.Popen(cmd, shell=True)
            handler.wait()
        except subprocess.CalledProcessError as exc:
            logger.exception("CalledProcessError exception. Cmd:{} return error code {}, the output is {}.".format(exc.cmd, exc.returncode, exc.output))
            return
        except OSError as e:
            logger.exception("OSError exception. Error num is {}, str error is {}, filename is {}".format(e.errno, e.strerror, e.filename))
            return
        except Exception as err:
            logger.exception(str(err))    
            return

    @staticmethod
    # compress the file
    def compressFile(file2Compress, zipfilePath, passwd=None):
        try:
            import subprocess
            exePath = os.path.join(parentdir, r"Tools\SevenZip\7za.exe")
            if (passwd):
                zipPwd = passwd
                cmd = r'"{}"'.format(exePath) + " a " + r'"{}"'.format(zipfilePath) + " " + r'"{}"'.format(file2Compress) + " -p" + zipPwd + " -y -sdel"
            else:
                cmd = r'"{}"'.format(exePath) + " a " + r'"{}"'.format(zipfilePath) + " " + r'"{}"'.format(file2Compress) + " -y -sdel"
            
            cmd = cmd.replace('\\', '/')
            #print("Call cmd {}".format(cmd))
            # subprocess.call(cmd, startupinfo=si)
            handler = subprocess.Popen(cmd, shell=True)
            handler.wait()
        except subprocess.CalledProcessError as exc:
            logger.exception("CalledProcessError exception. Cmd:{} return error code {}, the output is {}.".format(exc.cmd, exc.returncode, exc.output))
            return
        except OSError as e:
            logger.exception("OSError exception. Error num is {}, str error is {}, filename is {}".format(e.errno, e.strerror, e.filename))
            return
        except Exception as err:
            logger.exception(str(err))    
            return


    @staticmethod
    def copyFolder(src, dst, symlinks = False, ignore = None):
        try:
            import stat
            if not os.path.exists(dst):
                os.makedirs(dst)
                shutil.copystat(src, dst)
            lst = os.listdir(src)
            if ignore:
                excl = ignore(src, lst)
                lst = [x for x in lst if x not in excl]
            for item in lst:
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if symlinks and os.path.islink(s):
                    if os.path.lexists(d):
                        os.remove(d)
                    os.symlink(os.readlink(s), d)
                    try:
                        st = os.lstat(s)
                        mode = stat.S_IMODE(st.st_mode) 
                        os.lchmod(d, mode)
                    except:
                        pass # lchmod not available
                elif os.path.isdir(s):
                    FileUtils.copyFolder(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        except Exception as err:
            logger.exception(str(err))

    @staticmethod
    def copyTree(src, dst, symlinks=False, ignore=None):
        try:
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        except Exception as err:
            logger.exception(str(err))

    @staticmethod
    def getFileProperties(fname):
        """
        Read all properties of the given file return them as a dictionary.
        """
        propNames = ('Comments', 'InternalName', 'ProductName',
            'CompanyName', 'LegalCopyright', 'ProductVersion',
            'FileDescription', 'LegalTrademarks', 'PrivateBuild',
            'FileVersion', 'OriginalFilename', 'SpecialBuild')
    
        props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}
    
        try:
            # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
            fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
            props['FixedFileInfo'] = fixedInfo
            props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                    fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                    fixedInfo['FileVersionLS'] % 65536)
    
            # \VarFileInfo\Translation returns list of available (language, codepage)
            # pairs that can be used to retreive string info. We are using only the first pair.
            lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]
    
            # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
            # two are language/codepage pair returned from above
    
            strInfo = {}
            for propName in propNames:
                strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
                ## print str_info
                strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)
    
            props['StringFileInfo'] = strInfo
        except Exception as err:
            logger.exception(str(err))
        return props

    @staticmethod
    def downloadFileFromURL(url):
        try:
            get_response = requests.get(url,stream=True)
            #print(get_response.headers)
            #print(type(get_response.headers.get('Content-Length')))
            file_name  = url.split("/")[-1]
            with open(file_name, 'wb') as f:
                for chunk in get_response.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        #print( len(chunk))
                        f.write(chunk)
        except Exception as err:
            logger.exception("downloadFileFromURL() : %s" % str(err))

    @staticmethod
    def ExtractDigitalSignature(SignedFile, SignatureFile=None):
        pe = None
        try:
            '''
            Extracts the digital signature from Signed File
            When SignatureFile is not None, writes the signature to SignatureFile
            Returns the signature
            '''
        
            pe =  pefile.PE(SignedFile)
    
            address = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].VirtualAddress
            size = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].Size
    
            if address == 0:
                logger.info('Source file not signed')
                return ""
        
            signature = pe.write()[address+8:]
        
            if SignatureFile:
                f = open(SignatureFile, 'wb+')
                f.write(signature)
                f.close()
    
            pe.close()
            return signature.decode('utf-8', 'ignore')
        except Exception as e:
            logger.exception("ExtractDigitalSignature() : %s" % str(e))
            if(pe):
                pe.close()
            return ""

if __name__ == "__main__":
    path = "requirements.txt"
    import time
    # print(time.strftime("%Y-%m-%d", )
    timestr = FileUtils.getModifyTime(path)
    print(timestr)
    print(time.time())