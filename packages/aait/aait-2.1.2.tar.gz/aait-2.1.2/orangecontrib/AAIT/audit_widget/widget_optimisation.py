import os
import gc
import sys
import json
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWOptimisation import Optimisation
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.widgets.OWOptimisation import Optimisation
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver

def studies_out(optim, receiver):
     optim.Outputs.studies_out.send = receiver.receive_data
     optim.Outputs.studies_out.send(optim.current_data_previous_study)
     if len(receiver.received_data) > 0:
          if len(receiver.received_data[0]) != 4:
               return 1
     return 0

def check_out_pointer0(optim, receiver):
     optim.Outputs.out_pointer.send = receiver.receive_data
     optim.Outputs.out_pointer.send(str(id(optim)))
     if not isinstance(int(receiver.received_data), int):
          return 1
     return 0

def check_out_pointer1(optim, receiver):
     optim.Outputs.out_pointer1.send = receiver.receive_data
     optim.Outputs.out_pointer1.send(str(id(optim)))
     if  isinstance(int(receiver.received_data), (int)) == False:
          return 1
     return 0

def check_current_proposition_out(optim, receiver):
     optim.Outputs.current_proposition_out.send = receiver.receive_data
     optim.Outputs.current_proposition_out.send(optim.table)
     if len(receiver.received_data) > 0:
          if len(receiver.received_data[0]) != 4:
              return 1
     return 0

def check_widget_optimisation():
     # Def du nombres d'itérations
     domain = Domain([ContinuousVariable("nombre_iterations")])
     rows = [[1]]
     table = Table.from_list(domain, rows)

     # Def des espaces de recherches
     domain = Domain([ContinuousVariable("var"), ContinuousVariable("var1"), ContinuousVariable("var2")])
     rows = [[0, 0, 10], [10, 1, 100], [1, 0.1, 10]]
     table1 = Table.from_list(domain, rows)

     app = QApplication(sys.argv)
     optim = Optimisation()
     receiver = SignalReceiver()

     # on défini les données d'entrées du widget
     optim.set_data_search_space(table1)
     optim.set_data_number_iterations(table)

     if studies_out(optim, receiver) != 0:
          print("Erreur pour la sortie studies_out d'Optimisation")
          return 1

     if check_out_pointer0(optim, receiver) != 0:
          print("Erreur pour la sortie out pointer d'Optimisation")
          return 1

     if check_out_pointer1(optim, receiver) != 0:
          print("Erreur pour la sortie out pointer 1 d'Optimisation")
          return 1

     if check_current_proposition_out(optim, receiver) != 0:
          print("Erreur pour la sortie current proposition out d'Optimisation")
          return 1

     return 0

if __name__ == "__main__":
     check_widget_optimisation()