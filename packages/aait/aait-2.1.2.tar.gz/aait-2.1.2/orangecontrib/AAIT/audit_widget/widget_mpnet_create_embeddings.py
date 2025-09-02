import os
import sys
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWCreateEmbeddings import OWCreateEmbeddings
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_MPNET import OWModelMPNET
     from Orange.widgets.orangecontrib.AAIT.audit_widget.widgets_model import check_model_SentenceTransformer
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.widgets.OWCreateEmbeddings import OWCreateEmbeddings
     from orangecontrib.AAIT.widgets.OWModel_MPNET import OWModelMPNET
     from orangecontrib.AAIT.audit_widget.widgets_model import check_model_SentenceTransformer
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver


def check_create_embeddings(embeddings, model, receiver):
     text_var = StringVariable("content")
     domain = Domain([], metas=[text_var])
     table = Table.from_list(domain, [["Quel est la capital de la France ?"]])
     embeddings.set_model(model)
     embeddings.set_data(table)

     # Création d'une boucle d'attente pour simuler un chargement bloquant
     loop = QEventLoop()
     # Connecte la fin du chargement pour quitter la boucle
     def on_finish():
         loop.quit()
     embeddings.thread.finish.connect(on_finish)
     loop.exec_()
     embeddings.Outputs.data.send = receiver.receive_data
     embeddings.Outputs.data.send(embeddings.result)
     data = receiver.received_data
     if len(data) > 0 :
         if len(data[0]) == 768:
             return 0
         else:
             return 1
     else:
        return 1

def check_widget_mpnet_create_embeddings():
     app = QApplication(sys.argv)
     receiver = SignalReceiver()
     # Load and check model
     mpnet = OWModelMPNET()
     model = check_model_SentenceTransformer(mpnet, receiver, "MPNET")
     # Load and check CreateEmbeddings
     embeddings = OWCreateEmbeddings()
     if check_create_embeddings(embeddings,model, receiver) != 0:
           print("Erreur à la création des embeddings")
           return 1
     return 0


if __name__ == "__main__":
     check_widget_mpnet_create_embeddings()