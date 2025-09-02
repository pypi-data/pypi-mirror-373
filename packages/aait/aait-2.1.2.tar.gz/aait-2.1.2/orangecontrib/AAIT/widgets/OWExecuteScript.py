import os
import sys
import subprocess

import Orange.data
from Orange.data import Table, Domain, StringVariable
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from orangecontrib.AAIT.utils import thread_management


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWExecuteScript(widget.OWWidget):
    name = "Execute Script"
    description = "Locally execute the scripts contained in the column 'Script'."
    category = "AAIT - TOOLBOX"
    icon = "icons/owexecutescript.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owexecutescript.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owexecutescript.ui")
    want_control_area = False
    priority = 1060

    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.autorun:
            self.run()


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        # Data Management
        self.data = None
        self.autorun = True
        self.thread = None
        self.result = None
        self.post_initialized()

    def run(self):
        self.warning("")
        self.error("")

        # If Thread is already running, interrupt it
        if self.thread is not None:
            if self.thread.isRunning():
                self.thread.safe_quit()

        if self.data is None:
            return

        if not "Script" in self.data.domain:
            self.error("You do not have a 'Script' column, nothing happened.")
            return

        self.thread = thread_management.Thread(self.execute_scripts_in_table, self.data)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()


    def execute_scripts_in_table(self, table, progress_callback=None, argself=None):
        # Copy of input data
        data = table.copy()
        attr_dom = list(data.domain.attributes)
        metas_dom = list(data.domain.metas)
        class_dom = list(data.domain.class_vars)

        # Iterate on the data Table
        rows = []
        for i, row in enumerate(data):
            # Get the rest of the data
            features = [row[x] for x in attr_dom]
            targets = [row[y] for y in class_dom]
            metas = list(data.metas[i])
            # Execute the script for the given row
            output, error = self.execute_script(row["Script"].value)
            # Store the output / error
            new_row = features + targets + metas + [output, error]
            rows.append(new_row)
            if progress_callback is not None:
                progress_value = float(100 * (i + 1) / len(data))
                progress_callback(progress_value)
            if argself is not None:
                if argself.stop:
                    break

        # Create new Domain for new columns
        script_dom = [StringVariable("Script output"), StringVariable("Script error")]
        domain = Domain(attributes=attr_dom, metas=metas_dom + script_dom, class_vars=class_dom)
        # Create and return table
        out_data = Table.from_list(domain=domain, rows=rows)
        return out_data


    def execute_script(self, script):
        temp_path = "script_from_widget.py"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(script)
        try:
            result = subprocess.run(["python", temp_path], capture_output=True, text=True, check=True)
            output = result.stdout
            error = result.stderr
        except subprocess.CalledProcessError as e:
            output = e.stdout
            error = e.stderr
        os.remove(temp_path)
        return output, error


    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            self.result = result
            self.Outputs.data.send(result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        print("Scripts executed !")
        self.progressBarFinished()


    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWExecuteScript()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
