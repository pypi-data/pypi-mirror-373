from .consoles import *
from .logTab import logTab
from abstract_utilities import get_set_attr
consoles = [
               
            {"attr_name":"reactRunner","valueFunc":reactRunnerConsole,"label":"React Runner"},
            {"attr_name":"contentFinder","valueFunc":ContentFinderConsole,"label":"Content Finder"},                  
            {"attr_name":"apiConsole","valueFunc":apiTab,"label":"api console"},                   
            {"attr_name":"clipit","valueFunc":clipitTab,"label":"clipit"},
            {"attr_name":"windowMgr","valueFunc":windowManagerConsole,"label":"window mgr"},
            {"attr_name":"logConsole","valueFunc":logTab,"label":"Logs"}
            ]
def get_set_attr(parent,attr_name,value=None,valueFunc=None,default=False,*args,**kwargs):
    attr_value = getattr(parent,attr_name,default)
    if attr_value == False:
#        if value is None and valueFunc is not None:
#            value = valueFunc(*args,**kwargs)
        setattr(parent,attr_name,value)
        attr_value = getattr(parent,attr_name,default)
    return attr_value
def set_tab(parent,attr_name,label,tabFunc,value=None,valueFunc=None):
    child = get_set_attr(parent=parent,attr_name=attr_name,value=value,valueFunc=valueFunc)
    tabFunc(child,label)
def activate_consoles(parent,consoles,tabFunc=None):
    for console in consoles:
        console["tabFunc"]=tabFunc
        console["parent"]=parent
        set_tab(**console)
class abstractIde(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Tools")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        activate_consoles(self,consoles=consoles,tabFunc=self.tabs.addTab)
