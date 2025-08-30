from ..imports import *
# replace your AppRunner.start with this version
def _on_run(self):
    cmd = self.cmd_edit.text().strip()
    if not cmd:
        QtWidgets.QMessageBox.warning(self, "No command", "Please enter a command to run.")
        return
    # Example: bias environment for Python targets
    env = {"PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"}
    self.runner.start(cmd, cwd=None, env=env)
