from abstract_utilities import *
texts = """=== /home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/consoles/launcherWindowTab/initFuncs.py ===

'\n\nfrom .functions import (_on_run,)\n\ndef initFuncs(self):\n    try:\n        for f in (_on_run,):\n            setattr(self, f.__name__, f)\n    except Exception as e:\n        logger.info(f"{e}")\n    return self\n'


――――――――――――――――――



=== /home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/consoles/launcherWindowTab/imports.py ===

'from ..imports import*\nfrom ..appRunnerTab import appRunnerTab\nfrom ..logPaneTab import logPaneTab\n'


――――――――――――――――――



=== /home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/consoles/launcherWindowTab/main.py ===

'from .imports import *\nfrom .initFuncs import initFuncs\n# -----------------------------------------------------------------------------\n#  supervised child process runner ------------------------------------------------------------\n# -----------------------------------------------------------------------------\nclass launcherWindowTab(QtWidgets.QMainWindow):\n    def __init__(self):\n        super().__init__()\n        self.setWindowTitle("Universal App Launcher (supervised)")\n        self.resize(1000, 700)\n\n        # central dummy (replace with your real UI)\n        central = QtWidgets.QWidget(); self.setCentralWidget(central)\n        v = QtWidgets.QVBoxLayout(central)\n\n        # command entry + buttons\n        row = QtWidgets.QHBoxLayout()\n        self.cmd_edit = QtWidgets.QLineEdit()\n        self.cmd_edit.setPlaceholderText("Command to run (e.g. python -u your_app.py or /usr/bin/someapp)")\n        self.run_btn = QtWidgets.QPushButton("Run")\n        self.stop_btn = QtWidgets.QPushButton("Stop")\n        row.addWidget(self.cmd_edit); row.addWidget(self.run_btn); row.addWidget(self.stop_btn)\n        v.addLayout(row)\n\n        # toggleable bottom log pane\n        self.log_pane = logPaneTab(self)\n        self.log_pane.setVisible(True)  # start visible; you can default to False\n        v.addWidget(self.log_pane)\n\n        # runner\n        self.runner = appRunnerTab(self.log_pane, autorestart=True, parent=self)\n\n        # actions\n        self.run_btn.clicked.connect(self._on_run)\n        self.stop_btn.clicked.connect(self.runner.stop)\n\n        # menu / toolbar toggle\n        self.toggle_log_act = QtGui.QAction("Show/Hide Log", self, checkable=True, checked=True)\n        self.toggle_log_act.triggered.connect(lambda checked: self.log_pane.setVisible(checked))\n        tb = self.addToolBar("View"); tb.addAction(self.toggle_log_act)\n\n        # hotkey: F12 toggles log\n        QtGui.QShortcut(QtGui.QKeySequence("F12"), self, activated=lambda: self.toggle_log_act.trigger())\n\n\nlauncherWindowTab = initFuncs(launcherWindowTab)\n'




――――――――――――――――――



=== /home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/consoles/launcherWindowTab/functions/core_utils.py ===

'from ..imports import *\n# replace your AppRunner.start with this version\ndef _on_run(self):\n    cmd = self.cmd_edit.text().strip()\n    if not cmd:\n        QtWidgets.QMessageBox.warning(self, "No command", "Please enter a command to run.")\n        return\n    # Example: bias environment for Python targets\n    env = {"PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"}\n    self.runner.start(cmd, cwd=None, env=env)\n'


――――――――――――――――――
=== /home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/consoles/launcherWindowTab/functions/core_utils.py ===

'class AppRunner(QtCore.QObject):\n started = QtCore.pyqtSignal()\n stopped = QtCore.pyqtSignal(int) # exit code\n crashed = QtCore.pyqtSignal(int) # exit code\n\n def __init__(self, log_pane: LogPane, autorestart: bool = True, parent=None):\n super().__init__(parent)\n self.log = root_logger.getChild("AppRunner")\n self.p = QtCore.QProcess(self)\n self.p.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)\n self.p.readyReadStandardOutput.connect(self._drain)\n self.p.readyReadStandardError.connect(self._drain)\n self.p.started.connect(lambda: (self.log.info("child started pid=%s", self.p.processId()), self.started.emit()))\n self.p.errorOccurred.connect(lambda e: self.log.error("QProcess error: %s", e.name))\n self.p.finished.connect(self._on_finished)\n self.autorestart = autorestart\n self._last_cmd = None\n self._last_cwd = None\n self._last_env = None\n self.log_pane = log_pane\n\n # replace your AppRunner.start with this version\n def start(self, cmd: list[str] | str, cwd: str | None = None, env: dict | None = None, force_line_buffer: bool = True):\n # Save context for possible autorestart only after successful start\n self._last_cmd = None\n self._last_cwd = None\n self._last_env = None\n\n pe = QtCore.QProcessEnvironment.systemEnvironment()\n pe.insert("PYTHONUNBUFFERED", "1")\n pe.insert("PYTHONFAULTHANDLER", "1")\n for k, v in (env or {}).items():\n pe.insert(k, v)\n\n try:\n program, args = _split_command(cmd)\n\n if force_line_buffer:\n program, args = _wrap_stdbuf(program, args)\n\n self.p.setProcessEnvironment(pe)\n if cwd:\n self.p.setWorkingDirectory(cwd)\n\n self.log.info("launch: %s %s (cwd=%s)", program, " ".join(map(shlex.quote, args)), cwd or os.getcwd())\n self.p.start(program, args)\n\n if not self.p.waitForStarted(5000):\n err = self.p.error()\n self.log.error("failed to start: %s %s (QProcess error=%s)", program, args, err.name)\n self.log_pane.append_line(f"[ERROR] failed to start: {program} {args} (QProcess error={err.name})")\n return # don\'t arm autorestart on never-started process\n\n # only arm autorestart if we actually started\n self._last_cmd = cmd\n self._last_cwd = cwd\n self._last_env = env or {}\n\n except Exception as e:\n self.log.exception("start() exception while preparing command: %r", cmd)\n self.log_pane.append_line(f"[ERROR] start() exception: {e!r}")\n return\n\n\n def _drain(self):\n bs = self.p.readAllStandardOutput().data().decode(errors="replace")\n if bs:\n for line in bs.splitlines():\n root_logger.info("[child] %s", line)\n self.log_pane.append_line(line)\n bs = self.p.readAllStandardError().data().decode(errors="replace")\n if bs:\n for line in bs.splitlines():\n root_logger.error("[child:stderr] %s", line)\n self.log_pane.append_line(line)\n\n def _on_finished(self, code: int, status: QtCore.QProcess.ExitStatus):\n if status == QtCore.QProcess.ExitStatus.CrashExit:\n self.log.error("child crashed (code=%s)", code); self.crashed.emit(code)\n else:\n self.log.info("child exited (code=%s)", code); self.stopped.emit(code)\n if self.autorestart and self._last_cmd:\n self.log.warning("autorestart enabled; relaunching …")\n QtCore.QTimer.singleShot(1000, lambda: self.start(self._last_cmd, self._last_cwd, self._last_env))\n\n def stop(self):\n if self.p.state() != QtCore.QProcess.ProcessState.NotRunning:\n self.log.info("stopping child …")\n self.p.terminate()\n if not self.p.waitForFinished(3000):\n self.log.warning("terminate timed out; killing")\n self.p.kill()\n\n# ---------------- integrate into your UI ----------------\nclass LauncherWindow(QtWidgets.QMainWindow):\n def __init__(self):\n super().__init__()\n self.setWindowTitle("Universal App Launcher (supervised)")\n self.resize(1000, 700)\n\n # central dummy (replace with your real UI)\n central = QtWidgets.QWidget(); self.setCentralWidget(central)\n v = QtWidgets.QVBoxLayout(central)\n\n # command entry + buttons\n row = QtWidgets.QHBoxLayout()\n self.cmd_edit = QtWidgets.QLineEdit()\n self.cmd_edit.setPlaceholderText("Command to run (e.g. python -u your_app.py or /usr/bin/someapp)")\n self.run_btn = QtWidgets.QPushButton("Run")\n self.stop_btn = QtWidgets.QPushButton("Stop")\n row.addWidget(self.cmd_edit); row.addWidget(self.run_btn); row.addWidget(self.stop_btn)\n v.addLayout(row)\n\n # toggleable bottom log pane\n self.log_pane = LogPane(self)\n self.log_pane.setVisible(True) # start visible; you can default to False\n v.addWidget(self.log_pane)\n\n # runner\n self.runner = AppRunner(self.log_pane, autorestart=True, parent=self)\n\n # actions\n self.run_btn.clicked.connect(self._on_run)\n self.stop_btn.clicked.connect(self.runner.stop)\n\n # menu / toolbar toggle\n self.toggle_log_act = QtGui.QAction("Show/Hide Log", self, checkable=True, checked=True)\n self.toggle_log_act.triggered.connect(lambda checked: self.log_pane.setVisible(checked))\n tb = self.addToolBar("View"); tb.addAction(self.toggle_log_act)\n\n # hotkey: F12 toggles log\n QtGui.QShortcut(QtGui.QKeySequence("F12"), self, activated=lambda: self.toggle_log_act.trigger())\n\n def _on_run(self):\n cmd = self.cmd_edit.text().strip()\n if not cmd:\n QtWidgets.QMessageBox.warning(self, "No command", "Please enter a command to run.")\n return\n # Example: bias environment for Python targets\n env = {"PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"}\n self.runner.start(cmd, cwd=None, env=env)\n\n\n# entry point\nif __name__ == "__main__":\n app = QtWidgets.QApplication(sys.argv)\n w = LauncherWindow()\n w.show()\n sys.exit(app.exec())\n' ――――――――――――――――――

can this actually be a running python sheet that i can just input and run a script like i would idle?
"""
for line in texts.split('――――――――――――――――――'):
    line_spl = line.split('===')
    if len(line_spl)>1:
        path = line_spl[1]
        script = eatAll(line_spl[-1],"'")[1:-1]
        print(path)
        print(script)
