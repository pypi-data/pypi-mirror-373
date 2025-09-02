from setuptools import setup, find_packages

# Nom du package PyPI ('pip install NAME')
NAME = "aait"

# Version du package PyPI
VERSION = "2.1.2"  # la version doit être supérieure à la précédente sinon la publication sera refusée

# Facultatif / Adaptable à souhait
AUTHOR = "Orange community"
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = "Advanced Artificial Intelligence Tools is a package meant to develop and enable advanced AI functionalities in Orange"
LICENSE = ""

# 'orange3 add-on' permet de rendre l'addon téléchargeable via l'interface addons d'Orange
KEYWORDS = ["orange3 add-on",]

# Tous les packages python existants dans le projet (avec un __ini__.py)
PACKAGES = find_packages()
PACKAGES = [pack for pack in PACKAGES if "AAIT" in pack]
PACKAGES.append("orangecontrib")
print(PACKAGES)



# Fichiers additionnels aux fichiers .py (comme les icons ou des .ows)
PACKAGE_DATA = {
    "orangecontrib.AAIT.widgets": ["icons/*", "designer/*"],
    "orangecontrib.AAIT": ["fix_torch/*"],
    "orangecontrib.AAIT.utils.tools": ["owcorpus_ok.txt"],
    "orangecontrib.AAIT.audit_widget": ["dataTests/*"],
}
# /!\ les noms de fichier 'orangecontrib.hkh_bot.widgets' doivent correspondre à l'arborescence

# Dépendances

INSTALL_REQUIRES = [
    "torch",
    "sentence-transformers==5.0.0",
    "gpt4all[all]==2.8.2",
    "sacremoses==0.1.1",
    "transformers==4.51.3",
    "sentencepiece==0.2.0",
    "optuna",
    "spacy==3.7.6",
    "markdown",
    "python-multipart",
    "PyMuPDF==1.24.14",
    "chonkie==0.4.1",
    "GPUtil==1.4.0",
    "unidecode==1.3.8",
    "python-docx==1.1.2",
    "psutil",
    "thefuzz==0.22.1",
    "beautifulsoup4==4.12.3",
    "CATEGORIT"]


# Spécifie le dossier contenant les widgets et le nom de section qu'aura l'addon sur Orange
ENTRY_POINTS = {
    "orange.widgets": (
        "Advanced Artificial Intelligence Tools = orangecontrib.AAIT.widgets",
        "AAIT - API = orangecontrib.API.widgets",
        "AAIT - MODELS = orangecontrib.LLM_MODELS.widgets",
        "AAIT - LLM INTEGRATION = orangecontrib.LLM_INTEGRATION.widgets",
        "AAIT - TOOLBOX = orangecontrib.TOOLBOX.widgets",
        "AAIT - ALGORITHM = orangecontrib.ALGORITHM.widgets",
    )
}
# /!\ les noms de fichier 'orangecontrib.hkh_bot.widgets' doivent correspondre à l'arborescence

NAMESPACE_PACKAGES = ["orangecontrib"]

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      description=DESCRIPTION,
      license=LICENSE,
      keywords=KEYWORDS,
      packages=PACKAGES,
      package_data=PACKAGE_DATA,
      install_requires=INSTALL_REQUIRES,
      entry_points=ENTRY_POINTS,
      namespace_packages=NAMESPACE_PACKAGES,
      )
