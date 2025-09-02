import os
from AnyQt.QtWidgets import QPushButton, QApplication, QRadioButton, QComboBox,QCheckBox,QLineEdit


from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Output, Input
from Orange.data import Table, Domain, StringVariable


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import windows_utils,MetManagement
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
else:
    from orangecontrib.AAIT.utils import windows_utils, MetManagement
    from orangecontrib.AAIT.utils.import_uic import uic


class OWInputSelector(OWWidget):
    name = "Input Selector"
    description = "Select a file or a folder and assign it as a path"
    icon = "icons/in_or_out.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/in_or_out.png"
    category = "AAIT - TOOLBOX"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/ow_in_or_out_path.ui")
    priority = 10
    want_control_area = False
    class Inputs:
        input_table = Input("in data", Table)

    class Outputs:
        path = Output("out data", Table)


    select_folder_radio_button_checked: str = Setting("True")
    select_multiple_file_checked: str = Setting("False")
    new_file:str = Setting("False")
    combo_box_current_text: str=Setting("All (*.*)")
    line_edit_value:str=Setting("")
    def update_qt_view_from_settings(self):
        if str(self.select_folder_radio_button_checked) =="True":
            self.radioButton.setChecked(True)
            self.radioButton2.setChecked(False)
            self.checkBox.hide()
            self.comboBox.hide()
            self.checkBox_new_file.hide()
            return
        self.radioButton.setChecked(False)
        self.radioButton2.setChecked(True)

        if str(self.select_multiple_file_checked)=="False":
            self.checkBox.setChecked(False)
        else:
            self.checkBox.setChecked(True)

        if str(self.new_file)=="False":
            self.checkBox_new_file.setChecked(False)
            self.checkBox.setEnabled(True)
        else:
            self.checkBox_new_file.setChecked(True)
            self.checkBox.setEnabled(False)





        index = self.comboBox.findText(str(self.combo_box_current_text))
        if index != -1:
            self.comboBox.setCurrentIndex(index)
        else:
            self.comboBox.setCurrentIndex(0)  # Sélectionner le premier item

        self.checkBox.show()
        self.comboBox.show()
        self.checkBox_new_file.show()

    def update_setting_from_qt_view(self):
        if self.radioButton.isChecked():
            self.select_folder_radio_button_checked=True
            self.update_qt_view_from_settings()
            return
        self.select_folder_radio_button_checked = False
        if self.checkBox.isChecked():
            self.select_multiple_file_checked="True"
        else:
            self.select_multiple_file_checked = "False"

        if self.checkBox_new_file.isChecked():
            self.new_file="True"
        else:
            self.new_file = "False"


        self.combo_box_current_text=str(self.comboBox.currentText())
        self.update_qt_view_from_settings()


    # evite boucle infinie
    def on_text_changed(self,new_text):
        if new_text == self.combo_box_current_text:
            return  # Rien à faire, pas de vrai changement
        self.update_setting_from_qt_view()


    def __init__(self):
        super().__init__()
        self.selected_path = ""
        self.in_data = None


        self.setFixedWidth(700)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        self.radioButton=self.findChild(QRadioButton, 'radioButton')
        self.radioButton2 = self.findChild(QRadioButton, 'radioButton_2')
        self.checkBox = self.findChild(QCheckBox, 'checkBox')
        self.checkBox_new_file = self.findChild(QCheckBox, 'checkBox_2')
        self.comboBox = self.findChild(QComboBox, 'comboBox')
        self.pushButton = self.findChild(QPushButton, 'pushButton')
        self.lineEdit=self.findChild(QLineEdit,'lineEdit')
        self.lineEdit.setText(self.line_edit_value)

        # based on the string you can modify orders and add without problem
        file_types = [
            "All (*.*)",
            "Images (*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.svg;*.webp;*.heic;*.JPG;*.JPEG;*.PNG;*.BMP;*.GIF;*.TIFF;*.SVG;*.WEBP;*.HEIC)",
            "Documents (*.pdf;*.doc;*.docx;*.xls;*.xlsx;*.ppt;*.pptx;*.txt;*.rtf;*.odt;*.ods;*.odp;*.epub;*.PDF;*.DOC;*.DOCX;*.XLS;*.XLSX;*.PPT;*.PPTX;*.TXT;*.RTF;*.ODT;*.ODS;*.ODP;*.EPUB)",
            "Archives (*.zip;*.rar;*.7z;*.tar;*.gz;*.bz2;*.xz;*.iso;*.ZIP;*.RAR;*.7Z;*.TAR;*.GZ;*.BZ2;*.XZ;*.ISO)",
            "Audio (*.mp3;*.wav;*.ogg;*.flac;*.aac;*.m4a;*.wma;*.aiff;*.alac;*.MP3;*.WAV;*.OGG;*.FLAC;*.AAC;*.M4A;*.WMA;*.AIFF;*.ALAC)",
            "Vidéos (*.mp4;*.avi;*.mkv;*.mov;*.flv;*.wmv;*.mpeg;*.webm;*.3gp;*.MP4;*.AVI;*.MKV;*.MOV;*.FLV;*.WMV;*.MPEG;*.WEBM;*.3GP)",
            "Scripts (*.py;*.pyw;*.js;*.ts;*.html;*.htm;*.css;*.scss;*.sass;*.php;*.rb;*.pl;*.sh;*.c;*.cpp;*.h;*.hpp;*.java;*.swift;*.go;*.kt;*.rs;*.PY;*.PYW;*.JS;*.TS;*.HTML;*.HTM;*.CSS;*.SCSS;*.SASS;*.PHP;*.RB;*.PL;*.SH;*.C;*.CPP;*.H;*.HPP;*.JAVA;*.SWIFT;*.GO;*.KT;*.RS)",
            "Bases de données (*.db;*.sqlite;*.sql;*.csv;*.tsv;*.accdb;*.DB;*.SQLITE;*.SQL;*.CSV;*.TSV;*.ACCDB)",
            "3D/CAO (*.stl;*.obj;*.fbx;*.dae;*.blend;*.3ds;*.dxf;*.dwg;*.gltf;*.GLTF;*.STL;*.OBJ;*.FBX;*.DAE;*.BLEND;*.3DS;*.DXF;*.DWG)",
            "Fonts (*.ttf;*.otf;*.woff;*.woff2;*.eot;*.TTF;*.OTF;*.WOFF;*.WOFF2;*.EOT)",
            "Executables (*.exe;*.msi;*.bat;*.sh;*.apk;*.app;*.EXE;*.MSI;*.BAT;*.SH;*.APK;*.APP)",
            "Images disque (*.iso;*.img;*.dmg;*.ISO;*.IMG;*.DMG)",
            "Données (*.json;*.xml;*.yaml;*.yml;*.ini;*.cfg;*.JSON;*.XML;*.YAML;*.YML;*.INI;*.CFG)",
            "Vecteurs (*.svg;*.eps;*.pdf;*.ai;*.SVG;*.EPS;*.PDF;*.AI)",
            "Notes (*.md;*.markdown;*.MD;*.MARKDOWN)",

            # Fichiers individuels
            "Fichier JPG (*.jpg;*.JPG,*.jpeg;*.JPEG)",
            "Fichier PNG (*.png;*.PNG)",
            "Fichier BMP (*.bmp;*.BMP)",
            "Fichier GIF (*.gif;*.GIF)",
            "Fichier TIFF (*.tiff;*.TIFF)",
            "Fichier SVG (*.svg;*.SVG)",
            "Fichier WEBP (*.webp;*.WEBP)",
            "Fichier HEIC (*.heic;*.HEIC)",
            "Fichier PDF (*.pdf;*.PDF)",
            "Fichier DOC (*.doc;*.DOC)",
            "Fichier DOCX (*.docx;*.DOCX)",
            "Fichier XLS (*.xls;*.XLS)",
            "Fichier XLSX (*.xlsx;*.XLSX)",
            "Fichier PPT (*.ppt;*.PPT)",
            "Fichier PPTX (*.pptx;*.PPTX)",
            "Fichier TXT (*.txt;*.TXT)",
            "Fichier RTF (*.rtf;*.RTF)",
            "Fichier ODT (*.odt;*.ODT)",
            "Fichier ODS (*.ods;*.ODS)",
            "Fichier ODP (*.odp;*.ODP)",
            "Fichier EPUB (*.epub;*.EPUB)",
            "Fichier ZIP (*.zip;*.ZIP)",
            "Fichier RAR (*.rar;*.RAR)",
            "Fichier 7Z (*.7z;*.7Z)",
            "Fichier TAR (*.tar;*.TAR)",
            "Fichier GZ (*.gz;*.GZ)",
            "Fichier BZ2 (*.bz2;*.BZ2)",
            "Fichier XZ (*.xz;*.XZ)",
            "Fichier ISO (*.iso;*.ISO)",
            "Fichier MP3 (*.mp3;*.MP3)",
            "Fichier WAV (*.wav;*.WAV)",
            "Fichier OGG (*.ogg;*.OGG)",
            "Fichier FLAC (*.flac;*.FLAC)",
            "Fichier AAC (*.aac;*.AAC)",
            "Fichier M4A (*.m4a;*.M4A)",
            "Fichier WMA (*.wma;*.WMA)",
            "Fichier AIFF (*.aiff;*.AIFF)",
            "Fichier ALAC (*.alac;*.ALAC)",
            "Fichier MP4 (*.mp4;*.MP4)",
            "Fichier AVI (*.avi;*.AVI)",
            "Fichier MKV (*.mkv;*.MKV)",
            "Fichier MOV (*.mov;*.MOV)",
            "Fichier FLV (*.flv;*.FLV)",
            "Fichier WMV (*.wmv;*.WMV)",
            "Fichier MPEG (*.mpeg;*.MPEG)",
            "Fichier WEBM (*.webm;*.WEBM)",
            "Fichier 3GP (*.3gp;*.3GP)",
            "Fichier PY (*.py;*.PY)",
            "Fichier JS (*.js;*.JS)",
            "Fichier HTML (*.html;*.HTML)",
            "Fichier CSS (*.css;*.CSS)",
            "Fichier PHP (*.php;*.PHP)",
            "Fichier SH (*.sh;*.SH)",
            "Fichier JSON (*.json;*.JSON)",
            "Fichier XML (*.xml;*.XML)",
            "Fichier YAML (*.yaml;*.yml;*.YAML;*.YML)",
            "Fichier EXE (*.exe;*.EXE)",
            "Fichier MSI (*.msi;*.MSI)",
            "Fichier APK (*.apk;*.APK)",
            "Fichier APP (*.app;*.APP)",
            "Fichier DB (*.db;*.DB)",
            "Fichier SQLITE (*.sqlite;*.SQLITE)",
            "Fichier SQL (*.sql;*.SQL)",
            "Fichier CSV (*.csv;*.CSV)",
            "Fichier TSV (*.tsv;*.TSV)",
            "Fichier STL (*.stl;*.STL)",
            "Fichier OBJ (*.obj;*.OBJ)",
            "Fichier FBX (*.fbx;*.FBX)",
            "Fichier DAE (*.dae;*.DAE)",
            "Fichier 3DS (*.3ds;*.3DS)",
            "Fichier DXF (*.dxf;*.DXF)",
            "Fichier DWG (*.dwg;*.DWG)",
            "Fichier GLTF (*.gltf;*.GLTF)",
            "Fichier TTF (*.ttf;*.TTF)",
            "Fichier OTF (*.otf;*.OTF)",
            "Fichier WOFF (*.woff;*.WOFF)",
            "Fichier WOFF2 (*.woff2;*.WOFF2)",
            "Fichier EOT (*.eot;*.EOT)",
            "Fichier Markdown (*.md;*.markdown;*.MD;*.MARKDOWN)"
        ]
        self.comboBox.addItems(file_types)


        self.update_qt_view_from_settings()
        self.radioButton.clicked.connect(self.update_setting_from_qt_view)
        self.radioButton2.clicked.connect(self.update_setting_from_qt_view)
        self.checkBox.clicked.connect(self.update_setting_from_qt_view)
        self.checkBox_new_file.clicked.connect(self.update_setting_from_qt_view)

        self.comboBox.currentTextChanged.connect(self.on_text_changed)
        self.pushButton.clicked.connect(self.launch_fucntionalities)
        self.lineEdit.editingFinished.connect(self.update_line_edit_setting)

        if (len(self.line_edit_value)) == 0:
            self.radioButton.setEnabled(True)
            self.radioButton2.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.checkBox_new_file.setEnabled(True)
            if self.checkBox_new_file.isChecked():
                self.checkBox.setEnabled(False)
            else:
                self.checkBox.setEnabled(True)
        else:
            self.radioButton.setEnabled(False)
            self.radioButton2.setEnabled(False)
            self.checkBox.setEnabled(False)
            self.checkBox_new_file.setEnabled(False)
            self.comboBox.setEnabled(False)

    def update_line_edit_setting(self):
        self.line_edit_value=MetManagement.TransfromPathToStorePath(str(self.lineEdit.text()))
        if (len(self.line_edit_value)) == 0:
            self.radioButton.setEnabled(True)
            self.radioButton2.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.checkBox_new_file.setEnabled(True)
            if self.checkBox_new_file.isChecked():
                self.checkBox.setEnabled(False)
            else:
                self.checkBox.setEnabled(True)
        else:
            self.radioButton.setEnabled(False)
            self.radioButton2.setEnabled(False)
            self.checkBox.setEnabled(False)
            self.checkBox_new_file.setEnabled(False)
            self.comboBox.setEnabled(False)


    @Inputs.input_table
    def input_table(self, data):
        self.in_data = data
        if data is not None:
            self.launch_fucntionalities()






    def launch_fucntionalities(self):
        if self.line_edit_value!="":
            self.selected_path=MetManagement.TransfromStorePathToPath(self.line_edit_value)
            self.commit_path()
            return
        if str(self.select_folder_radio_button_checked) =="True":
            self.selected_path=self.select_folder()
            if self.selected_path is None:
                self.selected_path=""
            if self.selected_path=="":
                self.selected_path="error nothing selected"
            self.commit_path()
            return
        multi_select=False
        if str(self.select_multiple_file_checked)!="False":
            multi_select=True
        file_filter=str(self.combo_box_current_text)
        if str(self.new_file)=="False":
            self.selected_path=self.select_file(multi_select,file_filter)
        else:
            self.selected_path = self.select_new_file(file_filter)
        if self.selected_path is None:
            self.selected_path = ""
        if self.selected_path == "":
            self.selected_path = "error nothing selected"
        self.commit_path()
        return

    def select_file(self,multi_select,file_filtter):
        if os.name == 'nt':
            return windows_utils.select_file_ctypes(multi_select=multi_select, file_filter=file_filtter)
        print("a faire correctement sans qt sur mac (et linux")
        from AnyQt.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(
            self,  # parent
            "Sélectionner des fichiers",  # titre de la fenêtre
            "",  # répertoire initial
            "Tous les fichiers (*.*)"  # filtre
        )
        return files

    def select_new_file(self,file_filtter):
        if os.name == 'nt':
            return windows_utils.select_new_file_ctypes(file_filter=file_filtter)
        print("a faire correctement sans qt sur mac (et linux")
        from AnyQt.QtWidgets import QFileDialog
        files, _ = QFileDialog.getSaveFileName(
            self,  # parent
            "Créer un fichier",  # titre de la fenêtre
            "",  # répertoire initial
            "Tous les fichiers (*.*)"  # filtre
        )
        return str(files)




    def select_folder(self):
        if os.name=='nt':
            return windows_utils.select_folder_ctypes()
        # a faire correctement sans qt sur mac
        print("a faire correctement sans qt sur mac (et linux")
        from AnyQt.QtWidgets import QFileDialog
        return QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")

    def commit_path(self):
        self.error("")
        if self.in_data is not None:
            if "path" in self.in_data.domain or "path" in self.in_data.domain.metas:
                self.error("Path déjà dans les domaines d entrées.")
                self.Outputs.path.send(None)

        if not self.selected_path:
            return

        var = StringVariable("path")

        if self.in_data is not None:
            domain = Domain(
                self.in_data.domain.attributes,
                self.in_data.domain.class_vars,
                list(self.in_data.domain.metas) + [var]
            )
            new_table = Table.from_table(domain, self.in_data)
            new_meta_column = [self.selected_path] * len(new_table)
            new_table.metas[:, -1] = new_meta_column
        else:
            domain = Domain([], metas=[var])
            new_table = Table.from_list(domain, [[]])
            new_table.metas[0] = [self.selected_path]

        self.Outputs.path.send(new_table)


# Test standalone
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OWInputSelector()
    window.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
