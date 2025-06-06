import sys
import os
import re
from atomic_operator import AtomicOperator
import time

#customized built-in libraries
from basecase import BaseCase
from Utils.tmlog import TmLog
from Utils.systemUtils import SystemUtils

logger = TmLog.getLogger("ART_Runner")

class UserDefined(BaseCase):

    def __init__(self):
        try:
            super().__init__()
            self.name = "User Defined"
            self.detail = r"Detail: Launch Atomic Red Team from Specified Path"
            
        except Exception as err:
            logger.exception(str(err))

    def __del__(self):
        try:
            pass    
        except Exception as err:
            logger.exception(str(err))
    
    def run(self, atomicPath = None):
        try:
            ####
            if not atomicPath:
                self.displayToExecutionStatus(r'No valid path was provided. Test ended.')
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\"> </span>")
                return
            ####

            operator = AtomicOperator()
            list_result_Run = (operator.run(
                return_atomics=True,
                atomics_path=atomicPath,
                debug=True,
                command_timeout=300 #Test must finished within 5 minutes or it will be killed
            ))
            
            if len(list_result_Run):
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\">%s</span>" % ("Scenario Details at Atomic Red Team path [%s] . . . " % atomicPath))
            else:
                self.displayToExecutionStatus("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Total number of Attack Technique(s) in the scenario: 0" ))
                return

            #set the powershell execution policy to Unrestricted
            current_PS_Policy = getPowershellExecutionPolicy()
            if current_PS_Policy != "Unrestricted":
                setPowershellExecutionPolicy("Unrestricted")

            Runnable_atomic_test_dict = {}
            atomic_test_len = 0
            isInputArgumentExists = False
            
            for atomic in list_result_Run:
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:black;\">%s</span>" % ("Attack Technique: %s" % atomic.attack_technique))
                self.displayToExecutionStatus("Attack Technique Name: %s" % atomic.display_name)
                Runnable_atomic_test_dict[atomic.attack_technique] = []
                atomic_test_number = 0
                for test in atomic.atomic_tests:
                    lower_list = [x.lower() for x in test.supported_platforms]
                    if 'windows' in lower_list:
                        atomic_test_len += 1
                        atomic_test_number += 1
                        self.displayToExecutionStatus("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test number: %s" % atomic_test_number))
                        self.displayToExecutionStatus("Atomic Test name: %s" %test.name)
                        self.displayToExecutionStatus("Atomic Test description: %s" %test.description)
                        Runnable_atomic_test_dict[atomic.attack_technique].append(test.auto_generated_guid)
                        if test.input_arguments:
                            isInputArgumentExists = True
            self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\"> </span>")
            self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ("Total number of Attack Technique(s) in the scenario: %s" %len(list_result_Run)))
            self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ("Total number of runnable Atomic Test(s) in the scenario: %s" %atomic_test_len))
            logger.info("Runnable_atomic_test_dict for Windows: %s" %str(Runnable_atomic_test_dict))

            useDefaultValue = True
            if isInputArgumentExists:
                self.displayToExecutionStatus(r"Waiting for method to obtain value(s) for input argument(s) . . .")
                respond = self.askInputArgumentOption("Use Default Values for Input Arguments?")
                if respond:
                    useDefaultValue = True
                else:
                    useDefaultValue = False

            self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\">%s</span>" % ("Start Executing The Attack Technique(s) . . ."))
            time.sleep(10) #give 10 seconds for user to stop the execution
            for atomic in list_result_Run:
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\"> </span>")
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\">%s</span>" % ("Executing Attack Technique: %s" % atomic.attack_technique))
                self.displayToExecutionStatus("<span style=\" font-size:8pt; font-weight:600; color:black;\">%s</span>" % ("Attack Technique Name: %s" % atomic.display_name))
                self.displayToScenarioDetails("<span style=\" font-size:12pt; font-weight:600; color:blue;\">%s</span>" % ("Attack Technique: %s" % atomic.attack_technique))

                atomic_test_number = 0
                for test in atomic.atomic_tests:
                    lower_list = [x.lower() for x in test.supported_platforms]
                    if 'windows' not in lower_list:
                        continue
                    atomic_test_number += 1
                self.displayToExecutionStatus("<span style=\" font-size:8pt; font-weight:600; color:black;\">%s</span>" % ("Number of Atomic Test(s): %s" % atomic_test_number))

                atomic_test_number = 0
                for test in atomic.atomic_tests:
                    lower_list = [x.lower() for x in test.supported_platforms]
                    if 'windows' not in lower_list:
                        continue
                    atomic_test_number += 1
                    self.displayToExecutionStatus("<span style=\" font-size:10pt; font-weight:600; color:blue;\">%s</span>" % ("Executing Atomic Test number: %s" % atomic_test_number))
                    self.displayToExecutionStatus("<span style=\" font-size:8pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test name: %s" %test.name))
                    self.displayToExecutionStatus("<span style=\" font-size:8pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test description: %s" %test.description))

                    if "::triggers vision one" in test.description.lower():
                        if atomic_test_number == 1:
                            self.displayToV1Detections("<span style=\" font-size:12pt; font-weight:600; color:blue;\">%s</span>" % ("Attack Technique: %s" % atomic.attack_technique))
                        self.displayToV1Detections("<span style=\" font-size:10pt; font-weight:600; color:blue;\">%s</span>" % ("Atomic Test number: %s" % atomic_test_number))
                        self.displayToV1Detections("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test name: %s" %test.name))

                        InformationSearch = r"\:\:triggers vision one"
                        V1_Trigger = ""
                        match = None
                        match = re.search(InformationSearch, test.description, re.IGNORECASE)
                        if(match):
                            real_description = test.description[:match.start()]
                            V1_Trigger = test.description[match.start():]
                        else:
                            real_description = test.description
                        
                        real_description = real_description.replace(r"\n", "")
                        self.displayToV1Detections("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test description: %s" %real_description))
                        if len(V1_Trigger):
                            V1_Trigger = V1_Trigger.replace(r"\n", r"<br/>")
                            self.displayToV1Detections("<span style=\" font-size:10pt; font-weight:600; color:red;\">%s</span>" % (V1_Trigger))
                        self.displayToV1Detections("<span style=\" font-size:12pt; font-weight:600; color:blue;\"> </span>")

                    self.displayToScenarioDetails("<span style=\" font-size:10pt; font-weight:600; color:blue;\">%s</span>" % ("Atomic Test number: %s" % atomic_test_number))
                    self.displayToScenarioDetails("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test name: %s" %test.name))
                    new_description = test.description.replace(r"\n", r"<br/>")
                    self.displayToScenarioDetails("<span style=\" font-size:10pt; font-weight:600; color:black;\">%s</span>" % ("Atomic Test description: %s" %new_description))
                    self.displayToScenarioDetails("<span style=\" font-size:12pt; font-weight:600; color:blue;\"> </span>")

                    kwargs = {'kwargs':{}}
                    if test.input_arguments and (not useDefaultValue):
                        for arg in test.input_arguments:
                            self.displayToExecutionStatus("<span style=\" font-size:8pt; font-weight:600; color:red;\">%s</span>" % ("Waiting for input value of Atomic Test input_argument name: %s" %str(arg.name)))

                            received_value = self.getTextInput(message = "Please provide value for: %s" %str(arg.description), defaultValue = str(arg.default))
                            try:
                                new_value = None
                                if "integer" in str(arg.type).lower():
                                    new_value = int(received_value)
                                elif  "float" in str(arg.type).lower():
                                    new_value = float(received_value)
                                else:
                                    new_value = received_value
                            except:
                                new_value = arg.default

                            kwargs['kwargs'].update({str(arg.name):new_value})


                    #get pre_reqs
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:green;\">%s</span>" % ('-->Run Get Prerequisites for Attack Technique: [%s] with Atomic Test number [%s]' %(atomic.attack_technique, atomic_test_number)))
                    if len(test.dependencies):
                        self.displayToExecutionDetails("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ('Running the below comand(s):'))
                        for dependency in test.dependencies:
                            get_prereq_command = str(dependency.get_prereq_command)
                            self.displayToExecutionDetails(get_prereq_command + "<br/>")
                    dict_result_Run = {}
                    if len(kwargs['kwargs']):
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid],
                            get_prereqs=True,
                            atomics_path=atomicPath,
                            debug=True,
                            command_timeout=300, #Test must finished within 5 minutes or it will be killed
                            **kwargs
                        ))
                    else:
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid],
                            get_prereqs=True,
                            atomics_path=atomicPath,
                            debug=True,
                            command_timeout=300 #Test must finished within 5 minutes or it will be killed
                        ))
                    self.displayToExecutionDetails("<font color=%s size=+2>%s</font>" % ('black', 'Get Prerequisites Output:'))
                    result_Run = str(dict_result_Run)
                    result_Run = result_Run.replace(r"\n", r"<br/>")
                    result_Run = re.sub(r'cmd\.exe /c \"echo ::RUNNING THE BELOW COMMAND::\"', "<br/>", result_Run)
                    result_Run = re.sub(r'::RUNNING THE BELOW COMMAND::', "<br/>::RUNNING THE BELOW COMMAND::<br/><br/>", result_Run)
                    result_Run = result_Run.replace(" ", "&nbsp;")
                    self.displayToExecutionDetails(result_Run)
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ("--Get Prerequisites Ends--"))
                    
                    # run the technique
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:green;\">%s</span>" % ('-->Run Attack Technique: [%s] with Atomic Test number [%s]' %(atomic.attack_technique, atomic_test_number)))
                    if test.executor.command:
                        self.displayToExecutionDetails("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ('Running the below comand(s):'))
                        run_command = str(test.executor.command)
                        self.displayToExecutionDetails(run_command + "<br/>")
                    if len(kwargs['kwargs']):
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid], 
                            atomics_path=atomicPath,
                            debug=True,
                            command_timeout=300, #Test must finished within 5 minutes or it will be killed
                            **kwargs
                        ))
                    else:
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid], 
                            atomics_path=atomicPath,
                            debug=True,
                            command_timeout=300 #Test must finished within 5 minutes or it will be killed
                        ))
                    self.displayToExecutionDetails("<font color=%s size=+2>%s</font>" % ('black', 'Execution Output:'))
                    result_Run = str(dict_result_Run)
                    result_Run = result_Run.replace(r"\n", r"<br/>")
                    result_Run = re.sub(r'cmd\.exe /c \"echo ::RUNNING THE BELOW COMMAND::\"', "<br/>", result_Run)
                    result_Run = re.sub(r'::RUNNING THE BELOW COMMAND::', "<br/>::RUNNING THE BELOW COMMAND::<br/><br/>", result_Run)
                    result_Run = result_Run.replace(" ", "&nbsp;")
                    if len(result_Run) > 150000:
                        self.displayToExecutionDetails("TOO BIG OUTPUT DATA. CANNOT BE PRINTED.")
                    else:
                        self.displayToExecutionDetails(result_Run)
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ("--Attack Technique Execution Ends--"))
                    
                    # run the cleanup
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:green;\">%s</span>" % ('-->Run Cleanup for Attack Technique: [%s] with Atomic Test number [%s]' %(atomic.attack_technique, atomic_test_number)))
                    if test.executor.cleanup_command:
                        self.displayToExecutionDetails("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ('Running the below comand(s):'))
                        cleanup_command = str(test.executor.cleanup_command)
                        self.displayToExecutionDetails(cleanup_command + "<br/>")
                    if len(kwargs['kwargs']):
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid], 
                            atomics_path=atomicPath,
                            debug=True,
                            cleanup=True,
                            command_timeout=300, #Test must finished within 5 minutes or it will be killed
                            **kwargs
                        ))
                    else:
                        dict_result_Run = (operator.run(
                            test_guids=[test.auto_generated_guid], 
                            atomics_path=atomicPath,
                            debug=True,
                            cleanup=True,
                            command_timeout=300 #Test must finished within 5 minutes or it will be killed
                        ))
                    self.displayToExecutionDetails("<font color=%s size=+2>%s</font>" % ('black', 'Cleanup Output:'))
                    result_Cleanup = str(dict_result_Run)
                    result_Cleanup = result_Cleanup.replace(r"\n", r"<br/>")
                    result_Cleanup = re.sub(r'cmd\.exe /c \"echo ::RUNNING THE BELOW COMMAND::\"', "<br/>", result_Cleanup)
                    result_Cleanup = re.sub(r'::RUNNING THE BELOW COMMAND::', "<br/>::RUNNING THE BELOW COMMAND::<br/><br/>", result_Cleanup)
                    result_Cleanup = result_Cleanup.replace(" ", "&nbsp;")
                    self.displayToExecutionDetails(result_Cleanup)
                    self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:black;\">%s</span>" % ("--Attack Technique Cleanup Ends--"))
                    
                   
                self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:red;\">%s</span>" % ("End of Execution for Attack Technique: [%s]" %(atomic.attack_technique)))

            #revert the powershell execution policy to its original setting
            if current_PS_Policy != "Unrestricted":
                setPowershellExecutionPolicy(current_PS_Policy)
            
            self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:blue;\"> </span>")
            self.displayToExecutionStatus("<span style=\" font-size:12pt; font-weight:600; color:red;\">%s</span>" % ("End of Execution for all Attack Technique(s)"))

            return
        except Exception as err:
            self.displayToExecutionStatus("<span style=\" font-size:9pt; font-weight:600; color:red;\">Error: %s</span>" % (err))
            logger.error(str(err))
            return

def setPowershellExecutionPolicy(setting):
    try:
        powershellPath = SystemUtils.getExecutablePath("powershell.exe")
        strExecCmd = powershellPath + r' Set-ExecutionPolicy ' + setting + ' -Force'
        result = SystemUtils.runCmdReturnOutput(strExecCmd)   
    except Exception as err:
        logger.exception(str(err))

def getPowershellExecutionPolicy():
    try:
        powershellPath = SystemUtils.getExecutablePath("powershell.exe")
        strExecCmd = powershellPath + r' Get-ExecutionPolicy'
        result = SystemUtils.runCmdReturnOutput(strExecCmd)
        return result[0].strip()
    except Exception as err:
        logger.exception(str(err))
        return ""