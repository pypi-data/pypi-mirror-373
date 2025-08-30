from .imports import *
from .initFuncs import initFuncs

class launcherWindowTab(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal App Launcher (supervised)")
        self.resize(1100, 800)
        self._current_path: str | None = None

        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        # --- Editor toolbar ---
        etb = QtWidgets.QToolBar("Editor", self)
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, etb)
        new_act = etb.addAction("New")
        open_act = etb.addAction("Open…")
        saveas_act = etb.addAction("Save As…")
        etb.addSeparator()
        run_buf_act = etb.addAction("Run Code (F5)")
        run_sel_act = etb.addAction("Run Selection (F6)")

        # --- Code editor ---
        self.editor = QtWidgets.QPlainTextEdit()
        self._set_mono_font(self.editor)
        self.editor.setPlaceholderText("# Type Python here and press F5 to run the buffer, F6 for selection.\n")
        v.addWidget(self.editor, 2)

        # --- Command row (keep your existing command runner) ---
        row = QtWidgets.QHBoxLayout()
        self.cmd_edit = QtWidgets.QLineEdit()
        self.cmd_edit.setPlaceholderText("Command to run (e.g. python -u your_app.py or /usr/bin/someapp)")
        self.run_btn = QtWidgets.QPushButton("Run Cmd")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        row.addWidget(self.cmd_edit); row.addWidget(self.run_btn); row.addWidget(self.stop_btn)
        v.addLayout(row)

        # --- Log pane (existing) ---
        self.log_pane = logPaneTab(self)
        self.log_pane.setVisible(True)
        v.addWidget(self.log_pane, 1)

        # --- Runner (existing) ---
        self.runner = appRunnerTab(self.log_pane, autorestart=True, parent=self)

        # --- Actions / shortcuts ---
        self.run_btn.clicked.connect(self._on_run)
        self.stop_btn.clicked.connect(self.runner.stop)

        self.toggle_log_act = QtGui.QAction("Show/Hide Log", self, checkable=True, checked=True)
        self.toggle_log_act.triggered.connect(lambda checked: self.log_pane.setVisible(checked))
        tb = self.addToolBar("View"); tb.addAction(self.toggle_log_act)

        # Editor actions wired to handlers (bound via initFuncs)
        new_act.triggered.connect(self._on_new_buffer)
        open_act.triggered.connect(self._on_open_file)
        saveas_act.triggered.connect(self._on_save_file_as)
        run_buf_act.triggered.connect(self._on_run_code)
        run_sel_act.triggered.connect(self._on_run_selection)

        # Hotkeys
        QtGui.QShortcut(QtGui.QKeySequence("F12"), self, activated=lambda: self.toggle_log_act.trigger())
        QtGui.QShortcut(QtGui.QKeySequence("F5"), self, activated=self._on_run_code)
        QtGui.QShortcut(QtGui.QKeySequence("F6"), self, activated=self._on_run_selection)

launcherWindowTab = initFuncs(launcherWindowTab)
