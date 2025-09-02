import os
import sys
import ntpath

import Orange.data
from AnyQt.QtWidgets import QApplication, QLabel
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from AnyQt.QtWidgets import QCheckBox
from Orange.widgets.settings import Setting


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.llm import GPT4ALL
    from Orange.widgets.orangecontrib.AAIT.utils import  thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import getTempDir
else:
    from orangecontrib.AAIT.llm import GPT4ALL
    from orangecontrib.AAIT.utils import  thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from orangecontrib.AAIT.utils.MetManagement import getTempDir





@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWLLM4ALL(widget.OWWidget):
    name = "LLM Local 4 All"
    description = "Query a local LLM to get a response (deprecated -> use query llm instead)"
    category = "AAIT - LLM INTEGRATION"
    icon = "icons/llm4all.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/llm4all.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owllm4all.ui")
    want_control_area = False
    priority = 1090
    class Inputs:
        data = Input("Data", Orange.data.Table)
        model = Input("Model", str, auto_summary=False)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    stropen4all: str = Setting('False')  # ty
    @Inputs.data
    def set_data(self, in_data):
        """
        Setter for the input data.

        Parameters
        ----------
        in_data : Orange.data.Table
            The input table.

        Returns
        -------
        None

        """
        if not self.runable:
            return
        self.error("")
        # Set the input data
        self.data = in_data
        if self.data is None:
            return
        if "prompt" not in self.data.domain:
            self.error("input table need a prompt column")
            return
        if self.model==None:
            return
        # Run the widget
        self.run()
    def post_initialized(self):
        """
        used for overloading only
        """
        return

    @Inputs.model
    def set_model(self, model):
        """
        Setter for the model.

        Parameters
        ----------
        model : str
            The model.

        Returns
        -------
        None
        """
        if not self.runable:
            return
        self.error("")
        # Set the model
        self.model = ntpath.basename(model)
        if not self.model.endswith(".gguf"):
            self.error("Model needs to be in a gguf format.")
            return
        if self.model is None:
            return
        if self.data is None:
            self.error("widget need an input data with a prompt column")
            return
        if "prompt" not in self.data.domain:
            self.error("input table need a prompt column")
            return

        # Run the widget
        self.run()
    def __init__(self):
        """
        Initialize the widget.

        This function initializes the widget and sets up its basic properties.
        It also loads the user interface file and finds the label for the description.
        """

        super().__init__()
        self.runable=True
        # Initialize path management
        # This is used to store the current Orange Widgets (OWS) path
        self.current_ows = ""

        # Set the fixed width and height of the widget
        self.setFixedWidth(470)
        self.setFixedHeight(300)

        # Load the user interface file
        uic.loadUi(self.gui, self)

        # Find the label for the description
        self.label_description = self.findChild(QLabel, 'Description')
        self.checkbox_interface= self.findChild(QCheckBox, 'checkBox')
        if self.stropen4all == 'Coucicouca':
            self.stropen4all = 'False'
        if self.stropen4all=='False':
            self.checkbox_interface.setChecked(False)
        if self.stropen4all == 'True':
            self.checkbox_interface.setChecked(True)

        self.checkbox_interface.stateChanged.connect(self.on_checkbox_toggled)

        # Initialize data management
        # This is used to store the input data
        self.data = None
        self.model = None#"solar-10.7b-instruct-v1.0.Q6_K.gguf"
        self.result = None
        # Initialize thread management
        # This is used to handle the background thread
        self.thread = None
        self.post_initialized()

    def on_checkbox_toggled(self, state):
        if state == 2:  # Qt.Checked (valeur 2 pour "coché")
            self.stropen4all='True'
        elif state == 0:  # Qt.Unchecked (valeur 0 pour "décoché")
            self.stropen4all='False'
        elif state==1:
            self.stropen4all = 'Coucicouca'


    def run(self):
        """
        Run the widget.

        This function runs the widget by initializing the thread and starting it.
        It also handles the case where the thread is already running and interrupts it.

        Returns:
            None
        """
        if not self.runable:
            return
        # Clear the error message
        self.error("")


        chemin_fichier = os.path.join(getTempDir(), 'view4all.txt')
        if self.stropen4all=='False':
            # Vérifier si le fichier existe
            if os.path.exists(chemin_fichier):
                try:
                    # Supprimer le fichier
                    os.remove(chemin_fichier)
                except Exception as e:
                    print(f"Error : {e}")
            else:
                print(f"Le fichier n'existe pas : {chemin_fichier}")
        if self.stropen4all == 'True' or self.stropen4all == 'Coucicouca':
            if False==os.path.exists(chemin_fichier):
                try:
                    # Créer et écrire dans le fichier
                    with open(chemin_fichier, 'w') as fichier:
                        fichier.write("")
                except Exception as e:
                    print(f"Error : {e}")


        # If Thread is already running, interrupt it
        #if self.thread is not None:
        #    if self.thread.isRunning():
        #        self.thread.safe_quit()

        # If data is not provided, exit the function
        if self.data is None:
            return

        # Start progress bar
        self.progressBarInit()
        if os.name != "nt":
            self.warning("Your OS isn't Windows, please configure GPT4ALL to run as server")


        # Connect and start thread : main function, progress, result and finish
        # --> progress is used in the main function to track progress (with a callback)
        # --> result is used to collect the result from main function
        # --> finish is just an empty signal to indicate that the thread is finished
        #GPT4ALL.open_gpt_4_all(self.data)
        self.thread = thread_management.Thread(GPT4ALL.open_gpt_4_all, self.data, self.model, widget=self)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    @staticmethod
    def set_4allpath(path_name):
        """
        you can call this function to set specifical path of 4all
        """
        GPT4ALL.gpt4all_path=path_name

    def handle_progress(self, value: float) -> None:
        """
        Sets the progress bar value to the given value.

        Args:
            value (float): The value to set the progress bar to.

        Returns:
            None
        """
        # Set the progress bar value to the given value

        # The value parameter is a float between 0 and 1, representing
        # the current progress of the operation.
        self.progressBarSet(value)

    def handle_result(self, result):
        """
        Handles the result of the main function.

        Sends the result to the output data port if there are no errors.
        If there is an error, sends None to the output data port and prints
        the error message.

        Args:
            result (Any): The result of the main function.

        Returns:
            None
        """
        try:
            # Send the result to the output data port
            self.Outputs.data.send(result)
            self.result = result
        except Exception as e:
            # If there is an error, send None to the output data port
            # and print the error message
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        """
        Handles the finish signal of the main function.

        Prints a message indicating that the generation is finished and
        updates the progress bar to be finished.

        Returns:
            None
        """
        # Print a message indicating that the generation is finished
        print("Generation finished")
        # Set the progress bar to be finished
        self.progressBarFinished()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWLLM4ALL()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
