import os

import Orange.data
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QLineEdit
from AnyQt.QtWidgets import QComboBox

from sentence_transformers import SentenceTransformer

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.llm import chunking
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.llm import chunking
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWChunker(widget.OWWidget):
    name = "Text Chunker"
    description = "Create chunks on the column 'content' of a Table"
    icon = "icons/owchunking.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owchunking.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owchunking.ui")
    want_control_area = False
    priority = 1050
    category = "AAIT - LLM INTEGRATION"

    class Inputs:
        data = Input("Data", Orange.data.Table)
        model = Input("Model", SentenceTransformer, auto_summary=False)

    class Outputs:
        data = Output("Chunked Data", Orange.data.Table)

    chunk_size: str = Setting("300")
    overlap: str = Setting("100")
    mode: str = Setting("words")

    @Inputs.data
    def set_data(self, in_data):
        if in_data is None:
            self.Outputs.data.send(None)
            return
        self.data = in_data
        if self.autorun:
            self.run()

    @Inputs.model
    def set_model(self, in_model):
        self.model = in_model
        if self.autorun:
            self.run()

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)


        self.edit_mode = self.findChild(QComboBox, "comboBox")
        self.edit_mode.addItems(["words", "tokens", "sentence", "markdown"])
        index = self.edit_mode.findText(self.mode)
        self.edit_mode.setCurrentIndex(index)
        self.edit_mode.currentIndexChanged.connect(self.update_edit_mode)
        self.edit_chunkSize = self.findChild(QLineEdit, 'chunkSize')
        self.edit_chunkSize.setText(str(self.chunk_size))
        self.edit_chunkSize.textChanged.connect(self.update_chunk_size)
        self.edit_overlap = self.findChild(QLineEdit, 'QLoverlap')
        self.edit_overlap.setText(str(self.overlap))
        self.edit_overlap.textChanged.connect(self.update_overlap)


        # Data Management
        self.data = None
        self.model = None
        self.thread = None
        self.autorun = True
        self.result=None
        self.mode = self.edit_mode.currentText()
        self.chunk_size = self.edit_chunkSize.text() if self.edit_chunkSize.text().isdigit() else "300"
        self.overlap = self.edit_overlap.text() if self.edit_overlap.text().isdigit() else "100"

        self.post_initialized()

    def update_chunk_size(self, text):
        self.chunk_size = text

    def update_overlap(self, text):
        self.overlap = text

    def update_edit_mode(self, index):
        selected = self.edit_mode.itemText(index)
        self.mode = selected

    def run(self):
        # if thread is running quit
        """
        Main function of the widget. It segments the text into chunks of approximately
        400 words, stopping at sentence boundaries.

        If a thread is already running, it will be terminated.

        The function will also check if the input data contains a column named "content"
        and if it is a text variable. If not, an error message will be displayed.

        The function will then start a progress bar and a new thread with the
        chunk_data function. The thread will be connected to the progress bar,
        as well as to the result and finish signals.

        :return: None
        """

        if self.thread is not None:
            self.thread.safe_quit()

        if self.data is None:
            return

        if self.model is None:
            return

        # Verification of in_data
        self.error("")
        if not "content" in self.data.domain:
            self.error('You need a "content" column in input data')
            return

        if type(self.data.domain["content"]).__name__ != 'StringVariable':
            self.error('"content" column needs to be a Text')
            return

        # Start progress bar
        self.progressBarInit()

        # Connect and start thread
        self.thread = thread_management.Thread(chunking.create_chunks, self.data, self.model, int(self.chunk_size), int(self.overlap), str(self.mode))
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()


    def handle_progress(self, value: float) -> None:
        """
        Handles the progress signal from the main function.

        Updates the progress bar with the given value.

        :param value: (float): The value to set for the progress bar.

        :return: None
        """

        self.progressBarSet(value)

    def handle_result(self, result):
        """
        Handles the result signal from the main function.

        Attempts to send the result to the data output port. In case of an error,
        sends None to the data output port and displays the error message.

        :param result:
             Any: The result from the main function.

        :return:
            None
        """

        try:
            self.result=result
            self.Outputs.data.send(self.result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        """
        Handles the end signal from the main function.

        Displays a message indicating that the segmentation is complete and updates
        the progress bar to reflect the completion.

        :return:
            None
        """
        print("Chunking finished")
        self.progressBarFinished()

    def post_initialized(self):
        """
        This method is intended for post-initialization tasks after the widget has
        been fully initialized.

        Override this method in subclasses to perform additional configurations
        or settings that require the widget to be fully constructed. This can
        include tasks such as connecting signals, initializing data, or setting
        properties of the widget dependent on its final state.

        :return:
            None
        """
        pass

if __name__ == "__main__":

    #print(chunks1)

    # Advanced initialization with custom parameters
    from orangewidget.utils.widgetpreview import WidgetPreview
    from orangecontrib.text.corpus import Corpus
    corpus_ = Corpus.from_file("book-excerpts")
    WidgetPreview(OWChunker).run(corpus_)