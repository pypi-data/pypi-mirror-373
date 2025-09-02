import os
import sys
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWTranslation import OWTranslation
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_HelsinkiFrEn import OWModel_HelsinkiFrEn
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from Orange.widgets.orangecontrib.AAIT.audit_widget.widgets_model import check_model_Transformers
else:
     from orangecontrib.AAIT.widgets.OWTranslation import OWTranslation
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from orangecontrib.AAIT.widgets.OWModel_HelsinkiFrEn import OWModel_HelsinkiFrEn
     from orangecontrib.AAIT.audit_widget.widgets_model import check_model_Transformers

def check_translation(translation, model, receiver):
     text_var = StringVariable("content")
     domain = Domain([], metas=[text_var])
     table = Table.from_list(domain, [["Quelle est la capital de la France ?"]])

     translation.set_model(model)
     translation.set_data(table)
     # Création d'une boucle d'attente pour simuler un chargement bloquant
     loop = QEventLoop()
     # Connecte la fin du chargement pour quitter la boucle
     def on_finish():
         loop.quit()
     translation.thread.finish.connect(on_finish)
     loop.exec_()
     translation.Outputs.data.send = receiver.receive_data
     translation.Outputs.data.send(translation.result)
     data = receiver.received_data
     if len(data) > 0:
         if len(data[0]['Translation'].value) > 0:
             print("-- Sentence: Quelle est la capital de la France ?")
             print(f"-- Translation: {data[0]['Translation'].value}")
             return 0
         else:
             return 1
     else:
         return 1

def check_widget_traduction():
    print("\n##### Translation - beginning audit")
    app = QApplication(sys.argv)
    helsinki = OWModel_HelsinkiFrEn()
    receiver = SignalReceiver()
    translation = OWTranslation()
    model = check_model_Transformers(helsinki, receiver, "Helsinki")
    if check_translation(translation, model, receiver) != 0:
        print("Erreur à la traduction")
        return 1
    print("##### Translation - audit finished\n")
    return 0


if __name__ == "__main__":
     check_widget_traduction()