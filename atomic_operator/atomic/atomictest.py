import os

class AtomicTestInput:

    def __init__(self, 
    name        = None,
    description = None,
    type        = None,
    default     = None,
    value       = None,
    source      = None,
    destination = None,
    **kwargs):

        self.name        = name       
        self.description = description
        self.type        = type       
        self.default     = default    
        self.value       = value      
        self.source      = source     
        self.destination = destination


class AtomicExecutor:

    def __init__(self, 
    name               = None,
    command            = None,
    cleanup_command    = None,
    elevation_required = False,
    steps              = None,
    **kwargs):

        self.name               = name                 
        self.command            = command              
        self.cleanup_command    = cleanup_command    
        self.elevation_required = elevation_required 
        self.steps              = steps              


class AtomicDependency:

    def __init__(self, 
    description        = None,
    get_prereq_command = None,
    prereq_command     = None,
    **kwargs):

        self.description        = description       
        self.get_prereq_command = get_prereq_command
        self.prereq_command     = prereq_command    

class AtomicTest:
    """A single Atomic test object structure

    Returns:
        AtomicTest: A single Atomic test object
    """

    def __init__(self, 
    name                     = None,
    description              = None,
    supported_platforms      = None,
    auto_generated_guid      = None,
    executor                 = None,
    input_arguments          = None,
    dependency_executor_name = None,
    dependencies             = [],
    **kwargs):            
                                 
        self.name                     = name                    
        self.description              = description             
        self.supported_platforms      = supported_platforms     
        self.auto_generated_guid      = auto_generated_guid     
        self.executor                 = executor                
        self.input_arguments          = input_arguments         
        self.dependency_executor_name = dependency_executor_name
        self.dependencies             = dependencies            

        self. __attrs_post_init__()

    def __attrs_post_init__(self):
        if self.input_arguments:
            temp_list = []
            for key,val in self.input_arguments.items():
                argument_dict = {}
                argument_dict = val
                argument_dict.update({'name': key, 'value': val.get('default')})
                temp_list.append(AtomicTestInput(**argument_dict))
            self.input_arguments = temp_list
        if self.executor:
            executor_dict = self.executor
            if executor_dict.get('name') == 'manual':
                if not executor_dict.get('command'):
                    executor_dict['command'] = ''
            self.executor = AtomicExecutor(**executor_dict)
            executor_dict = None
        else:
            self.executor = []
        if self.dependencies:
            dependency_list = []
            for dependency in self.dependencies:
                dependency_list.append(AtomicDependency(**dependency))
            self.dependencies = dependency_list
