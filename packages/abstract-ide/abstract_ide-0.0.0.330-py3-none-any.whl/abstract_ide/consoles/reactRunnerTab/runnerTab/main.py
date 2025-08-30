from .imports import *
from .initFuncs import initFuncs
# === OPTIONAL: update the top text when selection changes ===

class runnerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.init_path = '/var/www/TDD/my-app'
        self.initializeInit()  # gives you: user_in, path_in, run_btn, rerun_btn, clear_btn,
                               # rb_all, rb_err, rb_wrn, cb_try_alt_ext, editor, etc.

        root = QVBoxLayout(self)
        
        # --- Top row ------------------------------------------------------------
        top = self.init_top_row_create()
        root.addLayout(top)

        # --- View toggles (no log output in this plain view) --------------------
        view_row = self.init_view_row_create()
        root.addLayout(view_row)


        tree_stack = self.init_tree_creation()
        dict_panel = self.init_dict_panel_creation()
        right_panel = self.init_text_editor_creation()        
        editor_row = self.init_horizontal_split(tree_stack,right_panel)
        stack_split = self.init_vertical_split_creation(dict_panel,editor_row)
        root.addWidget(stack_split, 1)
        # 4) Add this vertical splitter to your root layout
        
        # --- View wiring --------------------------------------------------------
        self.init_set_buttons(tree_stack)


        



runnerTab = initFuncs(runnerTab)
