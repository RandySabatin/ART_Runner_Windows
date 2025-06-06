import os
import subprocess
import copy
from .runner import Runner


class LocalRunner(Runner):
    """Runs AtomicTest objects locally
    """

    def __init__(self, atomic_test, test_path):
        """A single AtomicTest object is provided and ran on the local system

        Args:
            atomic_test (AtomicTest): A single AtomicTest object.
            test_path (Atomic): A path where the AtomicTest object resides
        """
        self.test = atomic_test
        self.test_path = test_path
        self.__local_system_platform = self.get_local_system_platform()

    def execute_process(self, command, executor=None, host=None, cwd=None, elevation_required=False):
        """Executes commands using subprocess

        Args:
            executor (str): An executor or shell used to execute the provided command(s)
            command (str): The commands to run using subprocess
            cwd (str): A string which indicates the current working directory to run the command
            elevation_required (bool): Whether or not elevation is required

        Returns:
            tuple: A tuple of either outputs or errors from subprocess
        """

        if not command:
            another_dict = {}
            another_dict['error'] =  "Error! Command is empty!"
            response_dict = (copy.deepcopy(another_dict))
            return response_dict

        _executor_list_ = ["powershell", "command_prompt", "sh", "bash"]
        if executor not in _executor_list_:
            another_dict = {}
            another_dict['error'] =  "Error! Executor name is not in %s!" %_executor_list_
            response_dict = (copy.deepcopy(another_dict))
            return response_dict
        
        command = f"{command.strip()}"

        command = self._replace_command_string(command, self.CONFIG.atomics_path, input_arguments=self.test.input_arguments, executor=executor)
        executor = self.command_map.get(executor).get(self.__local_system_platform)

        system32Path = r'C:\Windows\System32'
        if (r'C:\Windows\System32') in executor:
            system32Path = os.path.join(os.environ['SystemRoot'], 'SysNative' if os.path.exists(os.getenv("SystemDrive") + r"\Program Files (x86)") else 'System32')
            executor = executor.replace(r'C:\Windows\System32', system32Path)

        if len(command):
            bat_file_runner = os.path.join(cwd, "BAS_Demo.bat")
            new_command = command.splitlines()

            if 'powershell.exe' in  executor:
                ps1_script = os.path.join(cwd, "BAS_Demo.ps1")
                with open(ps1_script, 'w') as f:
                    for line in new_command:
                        if len(line.strip()):
                            f.write('%s\n' %(str(line)))

                with open(bat_file_runner, 'w') as f:
                    f.write('cmd.exe /c "echo ::RUNNING THE BELOW COMMAND::"\n')
                    f.write('powershell.exe "' + ps1_script + '"\n')
                executor = os.path.join(system32Path, "cmd.exe")

            elif 'cmd.exe' in executor:
                with open(bat_file_runner, 'w') as f:
                    for line in new_command:
                        if len(line.strip()):
                            f.write('cmd.exe /c "echo ::RUNNING THE BELOW COMMAND::"\n')
                            f.write('%s\n\n' %(str(line)))

            command = 'cmd.exe /c ""' + bat_file_runner + '""'

        CREATE_NO_WINDOW = 0x08000000
        p = subprocess.Popen(
            executor, 
            shell=False, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            env=os.environ, 
            cwd=cwd,
            creationflags=CREATE_NO_WINDOW, 
            universal_newlines=True
        )
        try:
            outs, errs = p.communicate(
                command + "\n", 
                timeout=Runner.CONFIG.command_timeout
            )
            response = self.print_process_output(command, p.returncode, outs, errs)
            response_dict = (copy.deepcopy(response))
            return response_dict
        except subprocess.TimeoutExpired as e:
            # Display output if it exists.
            if e.output:
                self.__logger.warning(e.output)
            if e.stdout:
                self.__logger.warning(e.stdout)
            if e.stderr:
                self.__logger.warning(e.stderr)
            self.__logger.warning("Command timed out!")

            # Kill the process.
            p.kill()

            another_dict = {}
            another_dict['error'] =  "Command timed out!"
            response_dict = (copy.deepcopy(another_dict))
            return response_dict

    def _get_executor_command(self):
        """Checking if executor works with local system platform
        """
        __executor = None
        self.__logger.debug(f"Checking if executor works on local system platform.")
        if self.__local_system_platform in self.test.supported_platforms:
            if self.test.executor.name != 'manual':
                __executor = self.command_map.get(self.test.executor.name).get(self.__local_system_platform)
        return __executor

    def start(self):
        return self.execute(executor=self.test.executor.name)
