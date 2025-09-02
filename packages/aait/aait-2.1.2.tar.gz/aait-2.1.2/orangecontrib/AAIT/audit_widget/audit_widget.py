import os
import sys
from Orange.data import Table, Domain, StringVariable,ContinuousVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.audit_widget import widgets_model, widget_optimisation, widget_mpnet_create_embeddings, widget_queryllm, widget_traduction, widget_spacy_md_fr_lemmatizer, widget_optimisationselection, widget_4all, widget_edit_table
else:
     from orangecontrib.AAIT.audit_widget import widgets_model, widget_optimisation, widget_mpnet_create_embeddings, widget_queryllm, widget_traduction, widget_spacy_md_fr_lemmatizer, widget_optimisationselection, widget_4all, widget_edit_table


if __name__ == "__main__":
    exit = False
    etat = []
    if widgets_model.check_models() != 0: # Don't run online
        etat.append("erreur in widgets_model \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widgets_model ok\n")

    if widget_optimisation.check_widget_optimisation() != 0:
        etat.append("erreur in widget_optimisation \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_optimisation ok\n")

    if widget_optimisationselection.check_widget_optimisationselection() != 0:
        etat.append("erreur in widget_optimisation_selection \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_optimisation_selection ok\n")

    if widget_mpnet_create_embeddings.check_widget_mpnet_create_embeddings() != 0:
        etat.append("erreur in widget_mpnet_create_embeddings \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_mpnet_create_embeddings ok\n")

    if widget_4all.check_widget_llm4all() != 0:
        etat.append("erreur in widget_llm4all \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_llm4all ok\n")

    if widget_queryllm.check_widget_solar_queryllm() != 0:
        etat.append("erreur in widget_queryllm \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_queryllm ok\n")

    if widget_traduction.check_widget_traduction() != 0:
        etat.append("erreur in widget_traduction \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_traduction ok\n")

    if widget_spacy_md_fr_lemmatizer.check_widget_lemmes() != 0:
        etat.append("erreur in widget_spacy_md_fr_lemmatizer \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_spacy_md_fr_lemmatizer ok\n")

    if widget_edit_table.check_widget_edit_table() != 0:
        etat.append("erreur in widget_edit_table  \n")
        if exit == True:
            exit(1)
    else:
        etat.append("widget_edit_table ok\n")

    if len(etat) != 0:
        print("\n")
        print("L'audit des widgets a été réalisé avec success")
    else:
        print("erreur dans les widgets suivants : \n")
        print(etat)
    exit(0)