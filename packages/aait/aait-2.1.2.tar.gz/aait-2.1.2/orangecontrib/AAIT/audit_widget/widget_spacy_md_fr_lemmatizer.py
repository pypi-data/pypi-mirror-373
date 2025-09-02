import os
import sys
from Orange.data import Table, Domain, StringVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWLemmatizer import OWLemmatizer
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_SpacyMD_FR import OWModelSpacyMDFR
     from Orange.widgets.orangecontrib.AAIT.audit_widget.widgets_model import check_model_path
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.widgets.OWLemmatizer import OWLemmatizer
     from orangecontrib.AAIT.widgets.OWModel_SpacyMD_FR import OWModelSpacyMDFR
     from orangecontrib.AAIT.audit_widget.widgets_model import check_model_path
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver


def check_lemmes_request(lemmatizer, model, receiver):
    # Define some data to send to the widget
    text_var = StringVariable("content")
    domain = Domain([], metas=[text_var])
    table = Table.from_list(domain, [["Quelle est la capital de la France ?"]])

    # Set the model and the request data in the widget
    lemmatizer.set_model(model)
    lemmatizer.set_request(table)

    # Create a loop to simulate a processing
    loop = QEventLoop()
    # Connect the end of the function to end the loop
    def on_finish():
        loop.quit()
    lemmatizer.thread.finish.connect(on_finish)
    # Start the loop
    loop.exec_()

    # Collect the results from the widget
    lemmatizer.Outputs.data.send = receiver.receive_data
    lemmatizer.Outputs.data.send(lemmatizer.result)
    data = receiver.received_data

    # Verify if lemmatization has happened : len(data) should be 8 with the input data (1 for each word + punct)
    if len(data) == 8 :
        return 0
    else:
        print("Quelque chose de bizarre s'est produit à la lemmatisation.")
        return 1


def check_lemmes_data(lemmatizer, model, receiver):
    # Define some data to send to the widget
    text_var = StringVariable("content")
    domain = Domain([], metas=[text_var])
    table = Table.from_list(domain, [["Quel est la capital de la France ?"]])

    # Set the model and the request data in the widget
    lemmatizer.set_model(model)
    lemmatizer.set_data(table)

    # Create a loop to simulate a processing
    loop = QEventLoop()
    # Connect the end of the function to end the loop
    def on_finish():
        loop.quit()
    lemmatizer.thread.finish.connect(on_finish)

    # Start the loop
    loop.exec_()

    # Collect the results from the widget
    lemmatizer.Outputs.data.send = receiver.receive_data
    lemmatizer.Outputs.data.send(lemmatizer.result)
    data = receiver.received_data

    # Verify if lemmatization has happened : len(data) should be 8 with the input data (1 for each word + punct)
    if data is not None :
        return 0
    else:
        print("Quelque chose de bizarre s'est produit à la lemmatisation.")
        return 1


def check_widget_lemmes():
    print("\n##### Lemmatization - beginning audit")
    # Define app and receiver signal
    app = QApplication(sys.argv)
    receiver = SignalReceiver()

    # Define and test Spacy model
    spacy = OWModelSpacyMDFR()
    model = check_model_path(spacy, receiver, "SpacyMD")

    # Define lemmatizer
    lemmatizer = OWLemmatizer()
    if check_lemmes_request(lemmatizer, model, receiver) != 0:
        print("Erreur sur la lemmatisation (request)")
        return 1
    if check_lemmes_data(lemmatizer, model, receiver) != 0:
        print("Erreur sur la lemmatisation (data)")
        return 1
    print("\n##### Lemmatization - audit finished")
    return 0


if __name__ == "__main__":
     check_widget_lemmes()