import os
import re

# Dossiers de base (à ajuster selon ta structure)
main_directory = "../../AAIT/"  # Dossier contenant les sous-dossiers avec widgets
widget_test_directory = os.path.join(main_directory, "audit_widget")  # Dossier contenant les tests
output_file = os.path.join(widget_test_directory, "readme.md")

# Regex pour détecter les classes OWWidget et leurs attributs name
widget_class_pattern = re.compile(r"class (\w+)\(widget\.OWWidget\)")
name_attribute_pattern = re.compile(r"name\s*=\s*\"(.*?)\"")

# Stockage des widgets trouvés
widgets_info = []

# Fonction pour analyser les fichiers et extraire les widgets
def analyze_widget_files():
    for root, _, files in os.walk(main_directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    class_match = widget_class_pattern.search(content)
                    name_match = name_attribute_pattern.search(content)
                    if class_match and name_match:
                        widget_name = name_match.group(1)
                        widgets_info.append({"name": widget_name, "class": class_match.group(1), "file": file_path})

# Fonction pour vérifier la présence de tests associés
def check_for_tests():
    for widget in widgets_info:
        test_found = False
        for root, _, files in os.walk(widget_test_directory):
            for file in files:
                if file.endswith(".py") and widget["class"] in open(os.path.join(root, file), encoding="utf-8").read():
                    test_found = True
                    break
            if test_found:
                break
        widget["test"] = "✅" if test_found else "❌"

# Fonction pour générer le fichier Markdown
def generate_markdown():
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("| Nom du Widget           | Test Existant | Intégré à Git | Remarque |\n")
        f.write("|-------------------------|---------------|----------------|----------|\n")
        for widget in widgets_info:
            f.write(f"| {widget['name']}      | {widget['test']}             | Oui            |          |\n")

# Exécution des fonctions
analyze_widget_files()
check_for_tests()
generate_markdown()

print(f"Tableau généré dans le fichier {output_file}")
