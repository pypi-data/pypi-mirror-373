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

from holado_core.common.finders.tools.find_context import FindContext,\
    ContainerFindContext, ListContainersFindContext
from holado_core.common.finders.tools.find_parameters import FindParameters
import logging
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.handlers.element_holder import ElementHolder
from holado_core.common.finders.tools.find_builder import FindBuilder
from holado_core.common.finders.tools.find_updater import FindUpdater
from holado_core.common.finders.tools.enums import FindType
from holado_core.common.exceptions.element_exception import NoSuchElementException,\
    TooManyElementsException
from holado_core.common.finders.tools.finder_info import FinderInfo
import abc

logger = logging.getLogger(__name__)


class Finder(object):
    """ Generic finder class.
    
    Any inheriting class should override the appropriate methods.
    Usually, methods _find_all_in_XXX are overridden, except _find_all_in_candidates.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, description=None):
        """
        @param description Description.
        """
        self.__description = description
        self.__inspector = None
        # self.__info = None
        self.__find_builder = None
        self.__find_updater = None
    
    @property
    def has_info(self):
        """
        @return If has finder information
        """
        return self.__info is not None
    
    @property
    def info(self):
        """
        @return Finder information
        """
        if self.__info == None:
            self.__info = FinderInfo()
        return self.__info
    
    @property
    def inspector(self):
        return self.__inspector
    
    @inspector.setter
    def inspector(self, inspector):
        """
        @param inspector Inspector that has created self finder
        """
        self.__inspector = inspector
    
    @property
    def find_builder(self):
        """
        Priors find builder from inspector
        @return Find builder
        """
        if self.__inspector != None:
            return self.__inspector.find_builder
        else:
            if self.__find_builder == None:
                self.__find_builder = FindBuilder()
            return self.__find_builder

    @find_builder.setter
    def find_builder(self, find_builder):
        """
        @param find_builder Find builder to use
        """
        self.__find_builder = find_builder
    
    @property
    def has_find_updater(self):
        """
        @return If has find updater
        """
        return self.__find_updater is not None
    
    @property
    def find_updater(self):
        """
        @return Find updater
        """
        if self.__find_updater == None:
            self.__find_updater = FindUpdater()
        return self.__find_updater
    
    @property
    def find_type(self):
        """
        @return Specific find method type. 
        """
        return self.find_updater.find_type
    
    @find_type.setter
    def find_type(self, find_type):
        """
        Set a specific find method type.
        @param find_type Find method type.
        """
        self.find_updater.find_type = find_type
    
    @property
    def finder_description(self):
        return f"{self.__class__.__name__}({self.element_description})"
    
    @property
    def element_description(self):
        """
        @return Description of the element(s) to find.
        """
        return self.__description
    
    
    def update_context(self, find_context):
        """
        @param find_context Context
        @param find_parameters Parameters
        @return Updated context 
        """
        if self.has_find_updater:
            return find_context.update(self.find_updater)
        else:
            return find_context
    
    def update_parameters(self, find_parameters):
        """
        @param find_parameters Parameters
        @return Updated parameters 
        """
        if self.has_find_updater:
            return find_parameters.update(self.find_updater)
        else:
            return find_parameters
    
    def find_in(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        return self.find(FindType.In, container, candidates, find_context, find_parameters)
    
    def find(self, find_type=None, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        Find element. 
        @param find_type Find type
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Element found.
        """
        if find_type is None:
            find_type = self.find_type
        find_context = self.find_builder.context(find_context, find_type, container, candidates)
        find_parameters = self.find_builder.parameters(find_parameters)

        # Process finders
        candidates = self._find_all(find_context=find_context, find_parameters=find_parameters)
        
        # Get element from candidates
        return self._get_element_from_list(candidates, find_parameters)
    
    def find_all_in(self, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        return self.find_all(FindType.In, container, candidates, find_context, find_parameters)
    
    def find_all(self, find_type=None, container=None, candidates=None, find_context=None, find_parameters=None):
        """
        Find all elements. 
        @param find_type Find type
        @param container Container from which make search.
        @param candidates Candidate containers.
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if find_type is None:
            find_type = self.find_type
        find_context = self.find_builder.context(find_context, find_type, container, candidates)
        find_parameters = self.find_builder.parameters(find_parameters)
        
        return self._find_all(find_context, find_parameters)
    
    def _find_all(self, find_context:FindContext, find_parameters:FindParameters):
        """
        Find all elements. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if isinstance(find_context, ContainerFindContext):
            return self._find_all_container(self.update_context(find_context), self.update_parameters(find_parameters))
        elif isinstance(find_context, ListContainersFindContext):
            return self._find_all_candidates(self.update_context(find_context), self.update_parameters(find_parameters))
        else:
            raise TechnicalException(f"[{self.finder_description}] Unmanaged find context '{find_context}'")
    
    def _find_all_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        """
        Find all elements for given container. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if self.find_type == FindType.Custom:
            # Unexpected case, self method should be overridden
            raise NotImplementedError(f"[{self.finder_description}] {self}")
        
        if find_context.find_type == FindType.In:
            return self._find_all_in_container(find_context, find_parameters)
        else:
            raise TechnicalException(f"[{self.finder_description}] Unmanaged find type '{find_context.find_type.name}'")
    
    def _find_all_candidates(self, find_context:ListContainersFindContext, find_parameters:FindParameters):
        """
        Find all elements for given candidates. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if self.find_type == FindType.Custom:
            # Default implementation is to iterate on containers
            return self._find_all_by_iteration(find_context, find_parameters)
        
        if find_context.find_type == FindType.In:
            return self._find_all_in_candidates(find_context, find_parameters)
        else:
            raise TechnicalException(f"[{self.finder_description}] Unmanaged find type '{find_context.find_type.name}'")
        
    
    def _find_all_by_iteration(self, find_context:ListContainersFindContext, find_parameters:FindParameters):
        """
        Find all elements by iterating on each container. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        res = []
        exc_intermediate = None
        
        prefix_logs = f"{self._get_indent_string_level(find_parameters)}[Finder({self.element_description}).findAll{'' if self.find_type is None else self.find_type.name}]"
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"{prefix_logs} -> begin with {find_context.nb_containers} candidates")
        
        # Iterate on each container context
        for index, container_find_context in enumerate(find_context):
            container_context = self.update_context(container_find_context)
            
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            
                logger.trace(f"{prefix_logs}     -> candidate {index}: {container_context.input_description}")
            
            try:
                cand_res = self._find_all(container_context, find_parameters)
                res.extend(cand_res)
                if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                    logger.trace(f"{prefix_logs}       -> candidate {index}   => {len(cand_res)} elements found")
            except NoSuchElementException as exc:
                if exc_intermediate is None:
                    exc_intermediate = exc
            
        if len(res) == 0 and exc_intermediate is not None:
            raise exc_intermediate

        if len(res) > 0:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_logs} -> return 0 candidate")
        else:
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"{prefix_logs} -> return {len(res)} candidates:\n{self._represent_candidates_output(res, 4)}")
        return res
        
    
    def _find_all_in_container(self, find_context:ContainerFindContext, find_parameters:FindParameters):
        """
        Find all elements in given container. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if find_context.find_type == FindType.In:
            # Unexpected case, self method should be overridden
            raise NotImplementedError(f"[{self.finder_description}] {self}")
        else:
            return self._find_all_container(find_context.with_find_type(FindType.In), find_parameters)
    
    def _find_all_in_candidates(self, find_context:ListContainersFindContext, find_parameters:FindParameters):
        """
        Find all elements in given candidates. 
        @param find_context Find context
        @param find_parameters Find parameters
        @return Elements found.
        """
        if find_context.find_type == FindType.In:
            # Default implementation is to iterate on containers
            return self._find_all_by_iteration(find_context, find_parameters)
        else:
            return self._find_all_candidates(find_context.with_find_type(FindType.In), find_parameters)
    
    def _get_element_from_list(self, candidates, find_parameters):
        if find_parameters.nth_element is not None:
            return self._get_nth_element_from_list(candidates, find_parameters)
        
        res = None
        
        # Analyze search result
        if len(candidates) == 1:
            res = candidates[0]
        elif len(candidates) > 1:
            raise TooManyElementsException(f"More than one ({len(candidates)}) {self.element_description} were found:\n{self.represent_candidate_output(candidates, 4)}")
        elif find_parameters.raise_no_such_element:
            raise NoSuchElementException(f"Unable to find {self.element_description}")
           
        return res
    
    def _get_nth_element_from_list(self, candidates, find_parameters):
        res = None
        
        if find_parameters.nth_element is not None and find_parameters.nth_element < 1:
            raise TechnicalException(f"Nth ({find_parameters.nth_element}) must be positive (>= 1)")
            
        # Analyze search result
        if len(candidates) < 1:
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException(f"Unable to find {self.element_description}: no candidates were found")
        elif len(candidates) < find_parameters.nth_element:
            msg = f"Unable to find {self.element_description}: Nth ({find_parameters.nth_element}) is greater than number of candidates ({len(candidates)})"
            if find_parameters.raise_no_such_element:
                raise NoSuchElementException(msg)
            else:
                logger.warning(self._get_indent_string_level(find_parameters) + msg)
        else:
            res = candidates[find_parameters.nth_element - 1]
           
        return res
    

    def verify_find_type_is_defined(self, error_message):
        """
        @param error_message Error message to raise is find type is not defined.
        """
        if self.find_type == FindType.Undefined:
            raise TechnicalException(f"[{self.element_description}] {error_message}")
    
    def is_valid_input(self, container, find_context, find_parameters):
        """
        @param container Container to validate
        @param find_context Find context
        @param find_parameters Find parameters
        @return True if container is valid according this finder
        """
        raise NotImplementedError(f"Unimplemented is_valid_input since inconsistent for [{self.finder_description}]")
        
    def _is_valid_input_in(self, finders, container, find_context, find_parameters):
        """
        Internal use, to check if container is valid in any finder of given list.
        @param finders Finder list
        @param container Container to validate
        @param find_parameters Find parameters
        @return True if container is valid for any finder
        """
        for finder in finders:
            try:
                if finder is not None:
                    if finder.is_valid_input(container, find_context, find_parameters):
                        return True
            except NotImplementedError:
                # continue
                pass
            
        return False
    
    def is_valid_output(self, element, find_context, find_parameters):
        """
        Return if element is valid according this finder.
        @param element Element to validate
        @param find_context Find context
        @param find_parameters Find parameters
        @return True if element is valid according this finder
        """
        raise NotImplementedError(f"Unimplemented is_valid_output since inconsistent for [{self.finder_description}]")
        
    def _is_valid_output_in(self, finders, element, find_context, find_parameters):
        """
        Internal use, to check if element is valid in any finder of given list.
        @param finders Finder list
        @param element Element to validate
        @param find_parameters Find parameters
        @return True if element is valid for any finder
        """
        for finder in finders:
            try:
                if finder is not None:
                    if finder.is_valid_output(element, find_context, find_parameters):
                        return True
            except NotImplementedError:
                # continue
                pass
            
        return False
    
    def _represent_candidates_output(self, candidates, indent):
        res_list = []
        for index, cand in candidates:
            res_list.append(f"{index}: {self._represent_candidate_output(cand)}")
        return Tools.indent_string(indent, "\n".join(res_list))

    def _represent_candidate_output(self, candidate):
        raise NotImplementedError(f"Missing implementation in {self}")
    
    def _get_indent_string_level(self, find_parameters: FindParameters=None, level=None):
        if level is not None:
            return Tools.get_indent_string(level * 4)
        elif find_parameters is not None:
            return self._get_indent_string_level(level=find_parameters.find_level)
        else:
            raise TechnicalException("level or find_parameters must be defined")

    def _add_candidates(self, res, candidates):
        for candidate in candidates:
            self._add_candidate(res, candidate)
    
    def _add_candidate(self, res, candidate):
        if not candidate in res:
            res.append(candidate)
    

    def _build_result(self, res, find_context, find_parameters):
        # Manage generic finders that don't heritate from ElementFinder, like ElseFinder
        if isinstance(res, ElementHolder):
            self._build_result_element(res, find_context, find_parameters)
        return res
    
    def _build_result_element(self, res, find_context, find_parameters):
        res.update_find_info(self, find_context, find_parameters)
        return res
    
    def _build_result_list(self, res, find_context, find_parameters):
        for el in res:
            self._build_result(el, find_context, find_parameters)
        return res
    
    
    