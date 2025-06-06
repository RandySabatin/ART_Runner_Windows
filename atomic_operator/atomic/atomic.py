import os
from .atomictest import AtomicTest
from ..models import Host

class Atomic:
    """A single Atomic data structure. Each Atomic (technique)
    will contain a list of one or more AtomicTest objects.
    """
    def __init__(self, 
    attack_technique = None,
    display_name     = None,
    path             = None,
    atomic_tests     = [],
    hosts            = [],
    **kwargs):

        self.attack_technique = attack_technique
        self.display_name     = display_name    
        self.path             = path            
        self.atomic_tests     = atomic_tests    
        self.hosts            = hosts           

        self.__attrs_post_init__()
        
    def __attrs_post_init__(self):
        if self.atomic_tests:
            test_list = []
            for test in self.atomic_tests:
                test_list.append(AtomicTest(**test))
            self.atomic_tests = test_list
