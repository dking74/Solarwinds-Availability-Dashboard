import dash_core_components as dcc

#######################################################################
#
#       NOTE: Classes in this module are not designed to be used
#             directly. They are used by other classes in order
#             to be more useful. DO NOT instantiate directly.
#
#######################################################################

class Widget():
    
    """Base class for all widgets"""
    def __init__(self, id, options):
        self.id = id
        self.options = options

    def __str__(self):
        """Return the string repr. of the object"""
        return "Class: {}; id: {}".format(Widget.__class__.__name__, self.id)
		
    def getComponent(self, **args):
		
        """Get the component created by subclasses"""
        return self._component(id=self.id, options=self.options, **args)

class Radio(Widget):
    
    """Class implementing radio items on html page"""
    def __init__(self, id, style={}, options=[]):
        super().__init__(id, options)
        self._component = dcc.RadioItems

class CheckList(Widget):
    
    """Class implmenting checklist on html page"""
    def __init__(self, id, style={}, options=[]):
        super().__init__(id, options)
        self._component = dcc.CheckList

class Dropdown(Widget):

    """Class implmenting dropdown on html page"""
    def __init__(self, id, style={}, options=[]):
        super().__init__(id, options)
        self._component = dcc.Dropdown

class TextArea(Widget):

    """Class implementing text area on html page"""
    def __init__(self, id, style={}, options=[]):
        super().__init__(id, options)
        self._component = dcc.TextArea

class Slider(Widget):

    """Class implementing slider on html page"""
    def __init__(self, id, style={}, options=[]):
        super().__init__(id, options)
        self._component = dcc.Slider


class Tab():

    """Class to implement tab in html page"""
    def __init__(self, id, options=[]):
        super().__init__(id, options)
        self._component = dcc.Tab
	