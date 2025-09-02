import os
import sys
import time
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWTranslation import OWTranslation
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_HelsinkiFrEn import OWModel_HelsinkiFrEn
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_HelsinkiEnFr import OWModel_HelsinkiEnFr
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_Mistral import OWModelMistral
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_MPNET import OWModelMPNET
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_Qwen import OWModelQwen
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_SolarUncensored import OWModelSolarUncensored
     from Orange.widgets.orangecontrib.AAIT.widgets.OWModel_SpacyMD_FR import OWModelSpacyMDFR

else:
     from orangecontrib.AAIT.widgets.OWTranslation import OWTranslation
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from orangecontrib.AAIT.widgets.OWModel_HelsinkiFrEn import OWModel_HelsinkiFrEn
     from orangecontrib.AAIT.widgets.OWModel_HelsinkiEnFr import OWModel_HelsinkiEnFr
     from orangecontrib.AAIT.widgets.OWModel_Mistral import OWModelMistral
     from orangecontrib.AAIT.widgets.OWModel_MPNET import OWModelMPNET
     from orangecontrib.AAIT.widgets.OWModel_Qwen import OWModelQwen
     from orangecontrib.AAIT.widgets.OWModel_Solar import OWModelSolar
     from orangecontrib.AAIT.widgets.OWModel_SolarUncensored import OWModelSolarUncensored
     from orangecontrib.AAIT.widgets.OWModel_SpacyMD_FR import OWModelSpacyMDFR


def check_model_SentenceTransformer(widget_model, receiver, name=""):
    # Création d'une boucle d'attente pour simuler un chargement
    loop = QEventLoop()
    # Connection de la fin du chargement pour quitter la boucle
    def on_finish():
        loop.quit()
    widget_model.thread.finish.connect(on_finish)
    # Lancement de la boucle d'attente
    loop.exec_()
    # Connection de la sortie "out_model" du widget
    widget_model.Outputs.out_model.send = receiver.receive_data
    # Envoi de l'attribut "model" du widget
    widget_model.Outputs.out_model.send(widget_model.model)
    model = receiver.received_data
    if model is None:
        print("Erreur au chargement du modèle " + name)
        exit(0)
    print(f"{name}: success")
    return model


def check_model_Transformers(widget_model, receiver, name):
    # Création d'une boucle d'attente pour simuler un chargement
    loop = QEventLoop()
    # Connection de la fin du chargement pour quitter la boucle
    def on_finish():
        loop.quit()
    widget_model.thread.finish.connect(on_finish)
    # Lancement de la boucle d'attente
    loop.exec_()
    # Connection de la sortie "out_models" du widget
    widget_model.Outputs.out_models.send = receiver.receive_data
    # Envoi de l'attribut "models" du widget
    widget_model.Outputs.out_models.send(widget_model.models)
    models = receiver.received_data
    if models is None:
        print("Erreur au chargement du modèle " + name)
        exit(0)
    print(f"{name}: success")
    return models


def check_model_path(widget_model, receiver, name):
    # Connection de la sortie "out_model_patj" du widget
    widget_model.Outputs.out_model_path.send = receiver.receive_data
    # Envoi de l'attribut "model_path" du widget
    widget_model.Outputs.out_model_path.send(widget_model.model_path)
    model_path = receiver.received_data
    if model_path is None:
        print("Erreur au chargement du modèle " + name)
        exit(0)
    print(f"{name}: success")
    return model_path


def check_models():
     app = QApplication(sys.argv)
     receiver = SignalReceiver()

     mpnet = OWModelMPNET()
     if check_model_SentenceTransformer(mpnet, receiver, "MPNET") is None:
        return 1
     helsinki_en_fr = OWModel_HelsinkiEnFr()
     if check_model_Transformers(helsinki_en_fr, receiver, "Helsinki EN-FR") is None:
        return 1
     helsinki_fr_en = OWModel_HelsinkiFrEn()
     if check_model_Transformers(helsinki_fr_en, receiver, "Helsinki FR-EN") is None:
         return 1
     solar = OWModelSolar()
     if check_model_path(solar, receiver, "Solar") is None:
        return 1
     solar_uncensored = OWModelSolarUncensored()
     if check_model_path(solar_uncensored, receiver, "Solar uncensored") is None:
        return 1
     qwen = OWModelQwen()
     if check_model_path(qwen, receiver, "QwenCoder") is None:
        return 1
     mistral = OWModelMistral()
     if check_model_path(mistral, receiver, "Mistral") is None:
        return 1
     spacy_md_fr = OWModelSpacyMDFR()
     if check_model_path(spacy_md_fr, receiver, "Spacy MD") is None:
         return 1
     return 0


if __name__ == "__main__":
     check_models()