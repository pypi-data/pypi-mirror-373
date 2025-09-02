import os
import gc
import sys
import json
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWOptimisationSelection import OWOptimisationSelection
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.widgets.OWOptimisationSelection import OWOptimisationSelection
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver


def check_out_data(optim, receiver):
     optim.radio_choice = 0
     optim.on_radio_changed()

     optim.Outputs.data.send = receiver.receive_data
     optim.Outputs.data.send(optim.data)
     print(receiver.received_data[0])
     if len(receiver.received_data) > 0:
          if len(receiver.received_data[0]) != 3:
              return 1
          return 0
     else:
          return 1

def check_widget_optimisationselection():
     id = str(123456789)

     # Def des espaces de recherches
     domain = Domain([ContinuousVariable("var"), ContinuousVariable("var1"), ContinuousVariable("var2")])
     rows = [[1, 1, 1]]
     table = Table.from_list(domain, rows)

     app = QApplication(sys.argv)
     optim = OWOptimisationSelection()
     receiver = SignalReceiver()

     # on défini les données d'entrées du widget
     optim.set_data(table)
     optim.set_pointer(id)

     if check_out_data(optim, receiver) != 0:
          print("Erreur pour la sortie d'Optimisation selection")
          return 1
     return 0

if __name__ == "__main__":
     check_widget_optimisationselection()