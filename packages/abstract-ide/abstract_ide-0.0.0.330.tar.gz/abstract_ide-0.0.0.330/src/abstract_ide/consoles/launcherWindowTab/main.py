from .imports import *
from .initFuncs import initFuncs
# -----------------------------------------------------------------------------
#  supervised child process runner ------------------------------------------------------------
# -----------------------------------------------------------------------------
class launcherWindowTab(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal App Launcher (supervised)")
        self.resize(1000, 700)

        # central dummy (replace with your real UI)
        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        # command entry + buttons
        row = QtWidgets.QHBoxLayout()
        self.cmd_edit = QtWidgets.QLineEdit()
        self.cmd_edit.setPlaceholderText("Command to run (e.g. python -u your_app.py or /usr/bin/someapp)")
        self.run_btn = QtWidgets.QPushButton("Run")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        row.addWidget(self.cmd_edit); row.addWidget(self.run_btn); row.addWidget(self.stop_btn)
        v.addLayout(row)

        # toggleable bottom log pane
        self.log_pane = logPaneTab(self)
        self.log_pane.setVisible(True)  # start visible; you can default to False
        v.addWidget(self.log_pane)

        # runner
        self.runner = appRunnerTab(self.log_pane, autorestart=True, parent=self)

        # actions
        self.run_btn.clicked.connect(self._on_run)
        self.stop_btn.clicked.connect(self.runner.stop)

        # menu / toolbar toggle
        self.toggle_log_act = QtGui.QAction("Show/Hide Log", self, checkable=True, checked=True)
        self.toggle_log_act.triggered.connect(lambda checked: self.log_pane.setVisible(checked))
        tb = self.addToolBar("View"); tb.addAction(self.toggle_log_act)

        # hotkey: F12 toggles log
        QtGui.QShortcut(QtGui.QKeySequence("F12"), self, activated=lambda: self.toggle_log_act.trigger())


launcherWindowTab = initFuncs(launcherWindowTab)
