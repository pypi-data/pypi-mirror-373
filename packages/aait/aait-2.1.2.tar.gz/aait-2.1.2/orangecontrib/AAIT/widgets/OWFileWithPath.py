import os
import sys
import math

import Orange.data
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from AnyQt.QtWidgets import QCheckBox
from Orange.widgets.settings import Setting
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWFileWithPath(widget.OWWidget):
    name = "File with Path"
    category = "AAIT - TOOLBOX"
    description = "Load some tabular data specified with a filepath ('.../data/example.xlsx')."
    icon = "icons/owfilewithpath.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owfilewithpath.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owfilewithpath.ui")
    want_control_area = False
    priority = 1060

    class Inputs:
        filepath = Input("Path", str, auto_summary=False)
        path_table = Input("Path Table", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    strloadAsString: str = Setting('False')


    @Inputs.filepath
    def set_filepath(self, in_filepath):
        if in_filepath is not None:
            self.filepath = in_filepath
            self.run()

    @Inputs.path_table
    def set_path_table(self, in_path_table):
        if in_path_table is not None:
            if "path" in in_path_table.domain:
                self.filepath = in_path_table[0]["path"].value
                self.run()
            else:
                self.warning("You need a 'path' variable from which the data will be loaded.")


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        self.checkbox_interface = self.findChild(QCheckBox, 'checkBox')
        if self.strloadAsString=="False":
            self.checkbox_interface.setChecked(False)
        else:
            self.checkbox_interface.setChecked(True)
        self.checkbox_interface.stateChanged.connect(self.on_checkbox_toggled)



        # Data Management
        self.filepath = None
        self.data = None
        self.autorun = True
        self.post_initialized()
    def on_checkbox_toggled(self):
        if self.checkbox_interface.isChecked():
            self.strloadAsString="True"
        else:
            self.strloadAsString="False"

    def safe_repr_val(self,var, val, missing_as_empty=False):
        """
        Version robuste de var.repr_val(val) :
        - gère les valeurs NaN/Inf
        - gère les erreurs de datetime.fromtimestamp (OSError invalid argument)
        """
        try:
            if var.is_string:
                s = var.str_val(val)  # pas de guillemets
            else:
                s = var.repr_val(val)
            if missing_as_empty and s == "?":
                return ""
            return s
        except (ValueError, OverflowError, OSError):
            # cas des TimeVariable avec timestamp invalide
            return "" if missing_as_empty else "?"

    def load_table_as_strings(self,filepath: str) -> Orange.data.Table:
        """
        Charge un fichier Orange et renvoie un Table où toutes les colonnes
        (features, class, metas) sont converties en StringVariable et placées en metas.
        """
        missing_as_empty=False # si on passe a True on met "" à la place de ?
        t = Orange.data.Table.from_file(filepath)
        dom = t.domain

        # 2) Toutes les variables d'origine
        all_vars = list(dom.attributes) + list(dom.class_vars) + list(dom.metas)

        # 3) Créer des StringVariable correspondantes
        new_metas = tuple(Orange.data.StringVariable(v.name) for v in all_vars)

        # 4) Domaine final : que des metas
        new_domain = Orange.data.Domain([], None, new_metas)

        # 5) Créer table vide
        t_str = Orange.data.Table.from_domain(new_domain, len(t))

        # 6) Remplissage sécurisé
        for j, src_var in enumerate(all_vars):
            col_data = t.get_column(src_var)
            text_vals = [self.safe_repr_val(src_var, v, missing_as_empty) for v in col_data]
            t_str.metas[:, j] = text_vals

        # 7) Métadonnées
        t_str.name = t.name
        t_str.ids = t.ids
        t_str.attributes = dict(getattr(t, "attributes", {}))

        return t_str
    def run(self):
        self.error("")
        self.warning("")

        if self.filepath is None:
            return

        #try:
        self.filepath = self.filepath.strip('"')

        if self.strloadAsString!="False":
            out_data = self.load_table_as_strings(self.filepath)
        else:
         out_data = Orange.data.Table.from_file(self.filepath)
        out_data.name = self.filepath
        #except Exception as e:
        #    self.error(f"An error occurred: the provided file path may not be supported ({e})")
        #    return

        self.Outputs.data.send(out_data)

    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWFileWithPath()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
