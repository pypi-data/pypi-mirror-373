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


class FindParameters(object):
    """ Find parameters
    """
    
    _do_analyze_time_finder = True
    _do_analyze_time_criteria = True

    __instance_default = None
    __instance_default_without_raise = None
    
    def __init__(self, raise_no_such_element=True, raise_intermediate_no_such_element=True, find_level=0, visibility=True, analyze_time_spent=True, 
                 redo=False, redo_ignored_exceptions=None, nb_max_elements=None, nth_element=None, add_valid_container=False):
        """
        Constructor
        @param raise_no_such_element If True, raise NoSuchElementException, else return None, when no element is found.
        @param raise_intermediate_no_such_element If True, raise NoSuchElementException, else return None, when no element is found in intermediate searches.
        @param find_level Find level, beginning at 0 and increasing at each sub-find.
        @param visibility Visibility of elements to find (None means any visibility).
        @param analyze_time_spent If True, analyze time spent in find.
        @param redo If redo
        @param redo_ignored_exceptions Ignorded exception in redo 
        @param nb_max_elements Number max of elements to find
        @param nth_element N'th element to find
        @param add_valid_container If True, add container to find result if it validates criteria
        """
        self.raise_no_such_element = raise_no_such_element
        self.raise_intermediate_no_such_element = raise_intermediate_no_such_element
        self.find_level = find_level
        self.visibility = visibility
        self.analyze_time_spent = analyze_time_spent
        self.redo = redo
        self.redo_ignored_exceptions = []
        if redo_ignored_exceptions is not None:
            self.redo_ignored_exceptions.extend(redo_ignored_exceptions)
        self.nb_max_elements = nb_max_elements
        self.nth_element = nth_element
        self.add_valid_container = add_valid_container
    
    def update(self, updater:FindUpdater):
        """
        @param updater Find updater
        @return Updated parameters
        """
        res = self
        if updater.has_context_value("analyze_time_spent"):
            res = res.with_analyze_time_spent(updater.get_context_value("analyze_time_spent"))
        if updater.has_context_value("nb_max_elements"):
            res = res.with_nb_max_elements(updater.get_context_value("nb_max_elements"))
        if updater.has_context_value("nth_element"):
            res = res.with_nth_element(updater.get_context_value("nth_element"))
        if updater.has_context_value("redo"):
            res = res.with_redo(updater.get_context_value("redo"))
        if updater.has_context_value("ignoring"):
            res = res.ignoring(updater.get_context_value("ignoring"))
        if updater.has_context_value("raise"):
            res = res.with_raise(updater.get_context_value("raise"))
        if updater.has_context_value("visibility"):
            res = res.with_visibility(updater.get_context_value("visibility"))
        return res

    def get_next_level(self, raise_exception=None):
        """
        @param raise_exception Whether raise exceptions or not
        @return Find parameter for next find level
        """
        res = copy.deepcopy(self)
        res.find_level += 1
        res.analyze_time_spent = False
        if raise_exception is not None:
            res.raise_no_such_element = raise_exception
            res.raise_intermediate_no_such_element = raise_exception
        return res
    
    def get_criteria_parameters(self):
        """
        @return Associated criteria parameters
        """
        res = copy.deepcopy(self)
        res.find_level += 1
        return res
    
    def with_visibility(self, visibility):
        """
        Note: if wanted visibility is the same, self instance is returned, else a new one is returned
        @param visibility Wanted visibility
        @return Same parameters but with given visibility
        """
        if visibility == self.visibility:
            return self
        else:
            res = copy.deepcopy(self)
            res.visibility = visibility
            return res
        
    def with_analyze_time_spent(self, analyze_time_spent):
        """
        Note: if wanted analyze_time_spent is the same, self instance is returned, else a new one is returned
        @param analyze_time_spent If analyze time spent
        @return Same parameters but with given analyze_time_spent
        """
        if analyze_time_spent == self.analyze_time_spent:
            return self
        else:
            res = copy.deepcopy(self)
            res.analyze_time_spent = analyze_time_spent
            return res
        
    def with_raise(self, raise_exception=True):
        """
        Note: if raise booleans are same, self instance is returned, else a new one is returned
        @param raise_exception Whether raise exceptions or not
        @return Same parameters but with raise
        """
        if self.raise_no_such_element == raise_exception and self.raise_intermediate_no_such_element == raise_exception:
            return self
        else:
            res = copy.deepcopy(self)
            res.raise_no_such_element = raise_exception
            res.raise_intermediate_no_such_element = raise_exception
            return res
        
    def without_raise(self):
        """
        Note: if raise booleans are already False, self instance is returned, else a new one is returned
        @return Same parameters but without raise
        """
        return self.with_raise(False)
    
    def with_redo(self, redo):
        """
        Note: if wanted redo is the same, self instance is returned, else a new one is returned
        @param redo If do redo
        @return Same parameters but with given redo
        """
        if redo == self.redo:
            return self
        else:
            res = copy.deepcopy(self)
            res.redo = redo
            res.redo_ignored_exceptions = self.redo_ignored_exceptions if redo else None
            return res
        
    def ignoring(self, exception_class):
        """
        @param exceptionType Type of exception to ignore.
        @return Same parameters but with given ignoring
        """
        if exception_class in self.redo_ignored_exceptions:
            return self
        else:
            res = copy.deepcopy(self)
            res.redo_ignored_exceptions.append(exception_class)
            return res
        
    def with_nb_max_elements(self, nb_max_elements):
        """
        Note: if wanted number max of elements is the same, self instance is returned, else a new one is returned
        @param nb_max_elements Number max of elements to find
        @return Same parameters but with given number max of elements
        """
        if nb_max_elements == self.nb_max_elements:
            return self
        else:
            res = copy.deepcopy(self)
            res.nb_max_elements = nb_max_elements
            return res
        
    def with_nth_element(self, nth_element):
        """
        Note: if wanted n'th element is the same, self instance is returned, else a new one is returned
        @param nth_element N'th element to find
        @return Same parameters but with given number max of elements
        """
        if nth_element == self.nth_element:
            return self
        else:
            res = copy.deepcopy(self)
            res.nth_element = nth_element
            return res
        
    def with_valid_container(self, add_valid_container):
        """
        @param add_valid_container N'th element to find
        @return Same parameters but with or without container validating criteria
        """
        if add_valid_container == self.add_valid_container:
            return self
        else:
            res = copy.deepcopy(self)
            res.add_valid_container = add_valid_container
            return res
        
    @staticmethod
    def default(raise_exception=True):
        """
        @param raise_exception Whether raise exceptions or not
        @return Default find parameters with given raiseability
        """
        if raise_exception:
            return FindParameters.default_with_raise()
        else:
            return FindParameters.default_without_raise()
    
    @staticmethod
    def default_with_raise():
        """
        @return Default find parameters with raises
        """
        if FindParameters.__instance_default is None:
            FindParameters.__instance_default = FindParameters(True, True, 0, True, FindParameters._do_analyze_time_finder, False, None, None, None, False)
        return FindParameters.__instance_default
    
    @staticmethod
    def default_without_raise():
        """
        @return Default find parameters without any raise
        """
        if FindParameters.__instance_default_without_raise is None:
            FindParameters.__instance_default_without_raise = FindParameters(False, False, 0, True, FindParameters._do_analyze_time_finder, False, None, None, None, False)
        return FindParameters.__instance_default_without_raise
    
    
    
    