import ctypes
import os
import sys
import Orange.data
from Orange.widgets.widget import Input, Output, OWWidget


class EndLoopWidget(OWWidget):
    name = "End Loop"
    description = "Widget to end a loop based on a predefined condition."
    icon = "icons/endloop.png"
    category = "AAIT - ALGORITHM"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/endloop.png"

    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owendloop.ui")
    want_control_area = False
    priority = 1011

    class Inputs:
        in_data = Input("Data In", Orange.data.Table)
        in_pointer = Input("End of the Loop Do-While", str, auto_summary=False)

    class Outputs:
        out_data = Output("Data Out", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.in_pointer = None

    @Inputs.in_data
    def set_data(self, data):
        self.error("")
        if data is None:
            self.data = None
            return
        if self.in_pointer is None:
            return

        self.data = data

        # cas ou on boucle temps que le nombre de ligne augmente
        if "True"==self.get_is_allow_to_change_line_number_from_start():
            print("autorise a changer de ligne")
            if self.get_nb_line() == self.get_nb_line_from_start():
                # on s'arrete
                self.Outputs.out_data.send(self.data)
                return
            # on boucle
            ctypes.cast(int(self.in_pointer), ctypes.py_object).value.set_data(self.data)
            return

        # Check if the number of lines has changed
        if self.get_nb_line() != self.get_nb_line_from_start():
            self.error("Error! You can't change the number of lines")
            return

        #check domain
        column_names_input_temp, column_types_input=self.get_column_name_and_type_from_start()
        column_names_output_temp, column_types_ouput = self.get_column_name_and_type()

        column_names_input=[]
        column_names_output = []
        for idx,element in enumerate(column_names_input_temp):
            column_names_input.append(element+ " ("+column_types_input[idx]+")")

        for idx, element in enumerate(column_names_output_temp):
            column_names_output.append(element + " (" + column_types_ouput[idx] + ")")

        if column_names_input != column_names_output:
            # Find elements that are only in one of the lists
            diff1 = [x for x in column_names_input if x not in column_names_output]
            diff2 = [x for x in column_names_output if x not in column_names_input]

            # Detect swapped elements
            swapped = [(x, y) for x, y in zip(column_names_input, column_names_output) if
                       x != y and x in column_names_output and y in column_names_input]

            # Function to format a list as a sentence
            def list_to_sentence(lst):
                if not lst:
                    return "None"
                if len(lst) == 1:
                    return lst[0]
                return ", ".join(lst[:-1]) + " and " + lst[-1]

            # Build the output message
            sentence = ""
            if diff1:
                sentence += f"The elements that are only in the beginning of the loop table are: {list_to_sentence(diff1)}.\n"
            if diff2:
                sentence += f"The elements that are only in the end of the loop table are: {list_to_sentence(diff2)}.\n"

            if swapped:
                swapped_sentence = ", ".join([f"{x} <-> {y}" for x, y in swapped])
                sentence += f"Detected swapped elements: {swapped_sentence}."
            self.error(sentence)
            return

        # input of the loop== output of the loop
        old_table=ctypes.cast(int(self.in_pointer), ctypes.py_object).value.get_in_data()
        idem=True
        for idx,element in enumerate(old_table):
            if element!=self.data[idx]:
                idem=False
                break

        # check if loop doesn't change anithing
        if idem:
            self.error("Error! your loop didn't change the data table")
            return




        if any(x > 0 for x in self.data.get_column("iter")):
            ctypes.cast(int(self.in_pointer), ctypes.py_object).value.set_data(self.data)
            return
        self.Outputs.out_data.send(self.data)




    @Inputs.in_pointer
    def set_pointer(self, pointer):
        self.in_pointer = int(pointer) if pointer else None

    def get_column_name_and_type_from_start(self):
        if self.in_pointer is not None:
            result = ctypes.cast(int(self.in_pointer), ctypes.py_object).value.get_column_name_and_type()
        return result

    def get_nb_line_from_start(self):
        result = 0
        if self.in_pointer is not None:
            result = ctypes.cast(int(self.in_pointer), ctypes.py_object).value.get_nb_line()
        return result

    def get_is_allow_to_change_line_number_from_start(self):
        result = "False"
        if self.in_pointer is not None:
            result = ctypes.cast(int(self.in_pointer), ctypes.py_object).value.is_allow_to_change_line_number()
        return result


    def get_nb_line(self):
        # Return the number of lines to compare with another widget
        if self.data is None:
            return 0
        return len(self.data)

    def get_column_name_and_type(self):
        # Return the name and type of 'data_in' to verify if they are the same
        if self.data is None:
            return [[], []]
        column_names = []
        column_types = []
        for element in self.data.domain:
            column_names.append(str(element))
            column_types.append(str(type(element)))
        return column_names, column_types





if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    obj = EndLoopWidget()
    obj.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()

