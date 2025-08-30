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
from ..imports import *
import tempfile, os, sys

def _set_mono_font(widget: QtWidgets.QPlainTextEdit):
    font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
    font.setPointSize(11)
    widget.setFont(font)

def _write_temp_script(text: str) -> str:
    # Keep file to allow re-runs; user can inspect tmp if wanted
    fd, path = tempfile.mkstemp(prefix="abstract_ide_", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def _guess_cwd(self) -> str | None:
    # Prefer directory of current file if any
    if getattr(self, "_current_path", None):
        return os.path.dirname(self._current_path)
    # Else, fall back to project-ish cwd if your app tracks one
    return None

# ---- UI actions bound via initFuncs -----------------------------------------

def _on_new_buffer(self):
    self._current_path = None
    self.editor.setPlainText("# New buffer\nprint('Hello from Abstract IDE')\n")
    self.statusBar().showMessage("New buffer", 2000)

def _on_open_file(self):
    path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Python file", "", "Python (*.py);;All (*)")
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())
        self._current_path = path
        self.statusBar().showMessage(f"Opened {path}", 3000)
    except Exception as e:
        QtWidgets.QMessageBox.critical(self, "Open failed", str(e))

def _on_save_file_as(self):
    path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", self._current_path or "", "Python (*.py);;All (*)")
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self._current_path = path
        self.statusBar().showMessage(f"Saved {path}", 3000)
    except Exception as e:
        QtWidgets.QMessageBox.critical(self, "Save failed", str(e))

def _on_run_code(self):
    code_text = self.editor.toPlainText()
    if not code_text.strip():
        QtWidgets.QMessageBox.information(self, "Nothing to run", "The editor is empty.")
        return
    # Save to a tmp script (don’t overwrite user file unless they Save As)
    script_path = _write_temp_script(code_text)
    env = {"PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"}
    py = sys.executable or "python3"
    cmd = f"{py} -u {shlex.quote(script_path)}"
    self.runner.start(cmd, cwd=_guess_cwd(self), env=env)

def _on_run_selection(self):
    cursor = self.editor.textCursor()
    selected = cursor.selectedText().replace('\u2029', '\n')  # QTextEdit selection line sep → newline
    if not selected.strip():
        QtWidgets.QMessageBox.information(self, "No selection", "Select some code and try again.")
        return
    script_path = _write_temp_script(selected)
    env = {"PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"}
    py = sys.executable or "python3"
    cmd = f"{py} -u {shlex.quote(script_path)}"
    self.runner.start(cmd, cwd=_guess_cwd(self), env=env)
