import os
import sys
import Orange.data
from AnyQt.QtWidgets import QApplication, QLineEdit, QCheckBox
from Orange.data import StringVariable, Table, Domain
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWFileFromDir(widget.OWWidget):
    name = "Find Files From Dir"
    description = ("Search files by extension or no for all files in a directory or subdirectories."
                   "You need a column 'input_dir' of the files.")
    category = "AAIT - TOOLBOX"
    icon = "icons/owfilesfromdir.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owfilesfromdir.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owfindfilesfromdir.ui")
    want_control_area = False
    priority = 1060
    extension = Setting("")
    recursive = Setting("False")

    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)


    @Inputs.data
    def set_path_table(self, in_data):
        if in_data is not None:
            if "input_dir" in in_data.domain:
                self.folderpath = in_data.get_column("input_dir")
                self.data = in_data
                self.run()
            else:
                self.warning("You need a 'input_dir' variable from which the data will be loaded.")


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(500)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        self.edit_extension = self.findChild(QLineEdit, 'lineEdit')
        self.edit_extension.setPlaceholderText("Extension (.docx, .pdf, .xslx, .csv, .json ...)")
        self.edit_extension.setText(self.extension)
        self.edit_extension.editingFinished.connect(self.update_parameters)
        self.comboBox = self.findChild(QCheckBox, 'checkBox')
        if self.recursive == "True":
            self.comboBox.setChecked(True)
        self.comboBox.stateChanged.connect(self.on_checkbox_toggled)
        # Data Management
        self.folderpath = None
        self.data = None
        self.autorun = True
        self.post_initialized()

    def update_parameters(self):
        self.extension = self.edit_extension.text()
        if self.folderpath is not None:
            self.run()

    def on_checkbox_toggled(self,state):
        self.recursive = "True"
        if state==0:
            self.recursive = "False"
        if self.folderpath is not None:
            self.run()


    def find_files(self):
        files_data = []
        for i in range(len(self.folderpath)):
            if self.recursive == "True":
                traversal = os.walk(self.folderpath[i])
            else:
                traversal = [(self.folderpath[i], [], os.listdir(self.folderpath[i]))]
            for root, _, files in traversal:
                for file in files:
                    if self.extension is None or file.lower().endswith(self.extension):
                        files_data.append([os.path.join(root, file).replace("\\","/")])
        return files_data

    def run(self):
        self.error("")
        self.warning("")
        if self.folderpath is None:
            self.error("No input dir in your data")
            return
        try:
            files_data = self.find_files()
            if len(files_data) == 0:
                self.Outputs.data.send(None)
                return
            X = [[] for _ in files_data]
            domain = Domain([], metas=[StringVariable("path")])
            table = Table.from_numpy(domain, X, metas=files_data)
            self.Outputs.data.send(table)
        except Exception as e:
            self.error(f"An error occurred: the provided file path may not be supported ({e})")
            return

    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWFileFromDir()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
