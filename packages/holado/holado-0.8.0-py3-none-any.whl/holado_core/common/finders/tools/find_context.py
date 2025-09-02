#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import copy
from holado_core.common.finders.tools.find_updater import FindUpdater
from holado_core.common.finders.tools.enums import FindType
from holado_core.common.handlers.element_holder import ElementHolder
from holado_core.common.finders.tools.find_builder import FindBuilder


class FindContext(object):
    """Base find context
    In usual use cases, the appropriate sub-class should be instantiated.
    """
    
    __instance_default = None
    
    def __init__(self, find_type=None, find_context=None):
        if find_type is not None:
            self.__find_type = find_type
        elif find_context is not None:
            self.__find_type = find_context.find_type
        else:
            self.__find_type = None
    
    @property
    def find_type(self):
        """
        @return Find type
        """
        return self.__find_type
    
    def update(self, updater: FindUpdater):
        """
        @param updater Find updater
        @return Updated context
        """
        res = copy.deepcopy(self)
        if updater.has_context_value("find_type"):
            res = res.with_find_type(updater.get_context_value("find_type"))
        if updater.has_context_value("update_root_container"):
            res = res.update_root_container(updater.get_context_value("update_root_container"))
        return res
    
    def update_root_container(self, do_update):
        """
        If needed, update the root container with container
        @param do_update If root has to be updated
        @return Same context but with given root
        """
        raise NotImplementedError("When using update_root_container method, the instantiated sub-class of FindContext must override it")

    def with_find_type(self, find_type):
        """
        Note: if wanted find type is the same, self instance is returned, else a new one is returned
        @param find_type Find type
        @return Same context but with given find type
        """
        if find_type == self.find_type:
            return self
        else:
            res = copy.deepcopy(self)
            res.find_type = find_type
            return res
    
    def get_find_type_container_description_prefix(self):
        """
        @return Prefix to container description associated to find type
        """
        if self.find_type == FindType.InParents:
            return "parents of "
        elif self.find_type == FindType.InChildren:
            return "children of "
        else:
            return ""

    def get_input_description(self, element=None):
        """
        @return Input description
        """
        if element is None:
            return "{NONE}"
        elif isinstance(element, ElementHolder):
            return f"[{element.description}]"
        else:
            return str(element)

    def get_input_complete_description(self, element=None):
        """
        @return Input complete description
        """
        if element is None:
            return "{NONE}"
        elif isinstance(element, ElementHolder):
            return f"[{element.complete_description}]"
        else:
            return str(element)

    def get_input_complete_description_and_details(self, element=None):
        """
        @return Input complete description and details
        """
        if element is None:
            return "{NONE}"
        elif isinstance(element, ElementHolder):
            return f"[{element.complete_description_and_details}]"
        else:
            return str(element)

    @staticmethod
    def default(find_type=None):
        """
        @return Default find context
        """
        if FindContext.__instance_default is None:
            FindContext.__instance_default = FindContext()
        res = FindContext.__instance_default
        
        if find_type is not None:
            res = res.with_find_type(find_type)
        
        return res
    
    
    
class WithRootContainerFindContext(FindContext):
    """
    Find context using containers.
    """

    def __init__(self, find_type=None, find_context=None):
        super().__init__(find_type, find_context)
        self.__root_container = None
        
        if isinstance(find_context, WithRootContainerFindContext):
            self.__root_container = find_context.root_container
        
    @property
    def root_container(self):
        """
        @return Root container
        """
        return self.__root_container
    
    def update(self, updater):
        res = super().update(updater)
        if updater.has_context_value("root_container"):
            res = res.with_root_container(updater.get_context_value("root_container"))
        return res
    
    def get_criteria_context(self):
        """
        @return Associated criteria context
        """
        return copy.deepcopy(self)
    
    def with_root_container(self, root_container):
        """
        Note: if wanted root is the same, self instance is returned, else a new one is returned
        @param __root_container Wanted root
        @return Same context but with given root
        """
        if root_container == self.__root_container:
            return self
        else:
            res = copy.deepcopy(self)
            res.__root_container = root_container
            return res
        
    
    
    
class ContainerFindContext(WithRootContainerFindContext):
    """
    Find context in a single container.
    """

    __instance_default = None

    def __init__(self, find_type=None, find_context=None):
        super().__init__(find_type, find_context)
        self.__container = None
        
        if isinstance(find_context, ContainerFindContext):
            self.__container = find_context.container
        
    @property
    def container(self):
        """
        @return Container
        """
        return self.__container
    
    def update(self, updater):
        res = super().update(updater)
        if updater.has_context_value("container"):
            res = res.with_container(updater.get_context_value("container"))
        return res
    
    def update_root_container(self, do_update):
        """
        If needed, update the root container with container
        @param do_update If root has to be updated
        @return Same context but with given root
        """
        if do_update and self.find_type != FindType.InParents:
            return self.with_root_container(self.container)
        else:
            return self
    
    def with_container(self, container, do_update=None):
        """
        Note 1: if wanted container is the same, self instance is returned, else a new one is returned
        Note 2: if root container is not already set, also set container as root
        @param container Wanted container
        @param do_update If root has to be updated
        @return Same context but with given container
        """
        if do_update is None and self.root_container is None:
            do_update = True
            
        if (container == self.container 
                and (not (do_update and self.find_type != FindType.InParents) or container == self.root_container) ):
            return self
        else:
            res = copy.deepcopy(self)
            res.__container = container
            return res.update_root_container(do_update)
        
    def get_input_description(self):
        return super().get_input_description(self.container)

    def get_input_complete_description(self):
        return super().get_input_complete_description(self.container)

    def get_input_complete_description_and_details(self):
        return super().get_input_complete_description_and_details(self.container)
    

    @staticmethod
    def default(find_type=None, container=None):
        """
        @return Default find context
        """
        if ContainerFindContext.__instance_default is None:
            ContainerFindContext.__instance_default = ContainerFindContext()
        res = ContainerFindContext.__instance_default
        
        if find_type is not None:
            res = res.with_find_type(find_type)
        if container is not None:
            res = res.with_container(container)
        
        return res
    
    
class ListContainersFindContext(WithRootContainerFindContext):
    """
    Find context in list of containers.
    """

    __instance_default = None

    def __init__(self, find_type=None, find_context=None):
        super().__init__(find_type, find_context)
        self.__containers = None
        self.__update_root_container_on_iteration = False
        
        if isinstance(find_context, ListContainersFindContext):
            self.__containers = find_context.containers
            self.__update_root_container_on_iteration = find_context.update_root_container_on_iteration
            
    def __iter__(self):
        self.__n = 0
        self.__find_builder = FindBuilder()
        return self

    def __next__(self):
        if self.__n < len(self.containers):
            res = self.__find_builder.context(find_context=self, container=self.containers[self.__n])
            self.__n += 1
            return res
        else:
            raise StopIteration
        
    @property
    def nb_containers(self):
        """
        @return Number of containers
        """
        if self.__containers is None:
            return 0
        else:
            return len(self.__containers)
        
    @property
    def containers(self):
        """
        @return Containers in which find element
        """
        return self.__containers
        
    @property
    def update_root_container_on_iteration(self):
        """
        @return If root container must be updated on iteration on containers
        """
        return self.__update_root_container_on_iteration
    
    def update(self, updater):
        res = super().update(updater)
        if updater.has_context_value("containers"):
            res = res.with_containers(updater.get_context_value("containers"))
        return res
    
    def update_root_container(self, do_update):
        """
        If needed, update the root container with container
        @param do_update If root has to be updated
        @return Same context but with given root
        """
        if do_update and self.find_type != FindType.InParents:
            return self.with_root_container(self.container)
        else:
            return self
    
    def with_containers(self, containers, do_update=None):
        """
        Note: if containers is not empty, returns a new context
        @param containers Wanted containers
        @param do_update If root has to be updated
        @return Same context but with given container
        """
        if do_update is None and self.root_container is None:
            do_update = True
            
        if containers == self.containers and do_update == self.update_root_container_on_iteration:
            return self
        else:
            res = copy.deepcopy(self)
            res.__containers = containers
            return res.with_update_root_container_on_iteration(do_update)
    
    def with_update_root_container_on_iteration(self, do_update=None):
        """
        If needed, update the root container on iteration
        @param do_update If root has to be updated
        @return Same context but with given container
        """
        if do_update == self.update_root_container_on_iteration:
            return self
        else:
            res = copy.deepcopy(self)
            res.__update_root_container_on_iteration = do_update
            return res
        
    def get_input_description(self):
        if self.containers is None or len(self.containers) == 0:
            return super().get_input_description(None)
        else:
            containers_descriptions = [super().get_input_description(c) for c in self.containers]
            return f"[{', '.join(containers_descriptions)}]"

    def get_input_complete_description(self):
        if self.containers is None or len(self.containers) == 0:
            return super().get_input_complete_description(None)
        else:
            containers_descriptions = [super().get_input_complete_description(c) for c in self.containers]
            return f"[{', '.join(containers_descriptions)}]"

    def get_input_complete_description_and_details(self):
        if self.containers is None or len(self.containers) == 0:
            return super().get_input_complete_description_and_details(None)
        else:
            containers_descriptions = [super().get_input_complete_description_and_details(c) for c in self.containers]
            return f"[{', '.join(containers_descriptions)}]"
    

    @staticmethod
    def default(find_type=None, containers=None):
        """
        @return Default find context
        """
        if ListContainersFindContext.__instance_default is None:
            ListContainersFindContext.__instance_default = ListContainersFindContext()
        res = ListContainersFindContext.__instance_default
        
        if find_type is not None:
            res = res.with_find_type(find_type)
        if containers is not None:
            res = res.with_containers(containers)
        
        return res
    
    
    