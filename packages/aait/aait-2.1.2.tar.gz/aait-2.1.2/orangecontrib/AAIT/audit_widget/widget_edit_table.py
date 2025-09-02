import os
import gc
import sys
import json
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWEditTable import OWEditTable
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.widgets.OWEditTable import OWEditTable
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver

def check_widget_edit_table():
     # Def des espaces de recherches
     domain = Domain([ContinuousVariable("var"), ContinuousVariable("var1"), ContinuousVariable("var2")])
     rows = [[0, 0, 10], [10, 1, 100], [1, 0.1, 10]]
     table = Table.from_list(domain, rows)
     app = QApplication(sys.argv)
     edittable = OWEditTable()
     receiver = SignalReceiver()
     edittable.set_data(table)
     edittable.Outputs.data.send = receiver.receive_data
     edittable.Outputs.data.send(edittable.updated_data)
     data = receiver.received_data
     if table.X.shape != data.X.shape:
         print("Erreur à l'édition des tables")
         return 1
     return 0

if __name__ == "__main__":
     check_widget_edit_table()