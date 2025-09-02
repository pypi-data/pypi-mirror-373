import os
import gc
import sys
import json
from Orange.data import Table, Domain, StringVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWLLM4ALL import OWLLM4ALL
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from Orange.widgets.orangecontrib.AAIT.audit_widget.widgets_model import check_model_path
else:
     from orangecontrib.AAIT.widgets.OWLLM4ALL import OWLLM4ALL
     from orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from orangecontrib.AAIT.audit_widget.widgets_model import check_model_path


def check_llm4all(llm4all, model, receiver):
     json_data = '[{"prompt": "Quand marseille a-t-il gagné la coupe d Europe? "}]'
     data = json.loads(json_data)
     text_var = StringVariable("prompt")
     domain = Domain([], metas=[text_var])
     rows = [[item["prompt"]] for item in data]
     table = Table.from_list(domain, rows)

     llm4all.set_data(table)
     llm4all.set_model(model)
     loop = QEventLoop()

     def on_finish():
         loop.quit()
     llm4all.thread.finish.connect(on_finish)
     loop.exec_()
     llm4all.Outputs.data.send = receiver.receive_data
     llm4all.Outputs.data.send(llm4all.result)
     data = receiver.received_data
     if data[0]["Answer"].value != None and len(data[0]["Answer"].value) > 0:
          return 0
     else:
          return 1


def check_solar(solar, receiver):
     solar.Outputs.model.send = receiver.receive_data
     solar.Outputs.model.send(solar.model_name)
     model = receiver.received_data
     if model == None:
         print("Erreur au chargement du model solar")
         exit(0)
     return model

def check_widget_llm4all():
     app = QApplication(sys.argv)
     llm4all = OWLLM4ALL()
     solar = OWModelSolar()
     receiver = SignalReceiver()
     model = check_model_path(solar, receiver, "solar")
     if "solar" not in model:
           print("Erreur au chargement du model solar")
           return 1
     if check_llm4all(llm4all, model, receiver) != 0:
           print("Erreur à la génération de réponse de 4all")
           return 1
     return 0


if __name__ == "__main__":
     check_widget_llm4all()






