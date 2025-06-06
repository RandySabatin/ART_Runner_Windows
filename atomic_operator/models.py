import os
from .base import Base
from .utils.exceptions import AtomicsFolderNotFound


class Config:
    def __init__(self, 
    atomics_path          = None,
    check_prereqs         = False,
    get_prereqs           = False,
    cleanup               = False,
    command_timeout       = 60,
    debug                 = False,
    prompt_for_input_args = False,
    kwargs                = {},
    copy_source_files     = True):

        self.atomics_path          = atomics_path         
        self.check_prereqs         = check_prereqs        
        self.get_prereqs           = get_prereqs          
        self.cleanup               = cleanup              
        self.command_timeout       = command_timeout      
        self.debug                 = debug                
        self.prompt_for_input_args = prompt_for_input_args
        self.kwargs                = kwargs               
        self.copy_source_files     = copy_source_files    
        

    def __attrs_post_init__(self):
        object.__setattr__(self, 'atomics_path', self.__get_abs_path(self.atomics_path))

    def __get_abs_path(self, value):
        return os.path.abspath(os.path.expanduser(os.path.expandvars(value)))

    def validate_atomics_path(self, attribute, value):
        value = self.__get_abs_path(value)
        if not os.path.exists(value):
            raise AtomicsFolderNotFound('Please provide a value for atomics_path that exists')



class Host:
    def __init__(self, 
    hostname           = None,
    username           = None,
    password           = None,
    verify_ssl         = False,
    ssh_key_path       = None,
    private_key_string = None,
    port               = 22,
    timeout            = 5):
        self.hostname           = hostname           
        self.username           = username           
        self.password           = password           
        self.verify_ssl         = verify_ssl         
        self.ssh_key_path       = ssh_key_path       
        self.private_key_string = private_key_string 
        self.port               = port               
        self.timeout            = timeout            
    

    def validate_ssh_key_path(self, attribute, value):
        if value:
            Base.get_abs_path(value)
