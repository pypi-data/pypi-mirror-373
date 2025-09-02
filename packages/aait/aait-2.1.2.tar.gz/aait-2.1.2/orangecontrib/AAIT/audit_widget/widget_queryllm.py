import os
import sys
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.widgets.OWQueryLLM import OWQueryLLM
    from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
    from Orange.widgets.orangecontrib.AAIT.audit_widget.widgets_model import check_model_path
    from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
    from orangecontrib.AAIT.widgets.OWQueryLLM import OWQueryLLM
    from orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
    from orangecontrib.AAIT.audit_widget.widgets_model import check_model_path
    from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver


def check_queryllm(widget_queryllm, model, receiver):
    text_var = StringVariable("prompt")
    domain = Domain([], metas=[text_var])
    table = Table.from_list(domain, [["### User: Quelle est la capital de la France ? Sois bref. ### Assistant:"]])
    widget_queryllm.set_model_path(model)
    widget_queryllm.set_data(table)

    # Création d'une boucle d'attente pour simuler un chargement bloquant
    loop = QEventLoop()
    # Connecte la fin du chargement pour quitter la boucle
    def on_finish():
        loop.quit()
    widget_queryllm.thread.finish.connect(on_finish)
    loop.exec_()
    widget_queryllm.Outputs.data.send = receiver.receive_data
    widget_queryllm.Outputs.data.send(widget_queryllm.result)
    data = receiver.received_data
    if len(data) > 0 :
        if not "Answer" in data.domain:
            return 1
        else:
            answer = data[0]["Answer"].value
            print("-- Question: Quelle est la capital de la France ?")
            print(f"-- Answer: {answer}")
            if answer == "" or answer == "?":
                return 1
            else:
                return 0
    else:
        return 1

def check_widget_solar_queryllm():
    print("\n##### QueryLLM - beginning audit")
    app = QApplication(sys.argv)
    receiver = SignalReceiver()
    # Load and check model
    solar = OWModelSolar()
    model = check_model_path(solar, receiver, "Solar")
    # Load and check CreateEmbeddings
    widget_queryllm = OWQueryLLM()
    if check_queryllm(widget_queryllm, model, receiver) != 0:
       print("Erreur à la génération de réponse (QueryLLM)")
       return 1
    print("##### QueryLLM - audit finished\n")
    return 0


if __name__ == "__main__":
     check_widget_solar_queryllm()