from .imports import *
from .initFuncs import initFuncs
from ..logPaneTab import logPaneTab
# -----------------------------------------------------------------------------
#  supervised child process runner ------------------------------------------------------------
# -----------------------------------------------------------------------------
class appRunnerTab(QtCore.QObject):
    started = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal(int)      # exit code
    crashed = QtCore.pyqtSignal(int)      # exit code

    def __init__(self, log_pane=None, autorestart: bool = True, parent=None):
        super().__init__(parent)
        self.log = root_logger.getChild("AppRunner")
        self.p = QtCore.QProcess(self)
        self.p.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
        self.p.readyReadStandardOutput.connect(self._drain)
        self.p.readyReadStandardError.connect(self._drain)
        self.p.started.connect(lambda: (self.log.info("child started pid=%s", self.p.processId()), self.started.emit()))
        self.p.errorOccurred.connect(lambda e: self.log.error("QProcess error: %s", e.name))
        self.p.finished.connect(self._on_finished)
        self.autorestart = autorestart
        self._last_cmd = None
        self._last_cwd = None
        self._last_env = None
        self.log_pane = log_pane or logPaneTab

appRunnerTab = initFuncs(appRunnerTab)
