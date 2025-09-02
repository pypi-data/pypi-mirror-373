import json
import Orange


def parse_tab_file_orange(file_path):
    """
    Lit un fichier .tab avec Orange et renvoie la liste d'infos sur les variables.
    Chaque élément de cette liste est un dict du style:
    {
        "name": <str>,
        "type": <"continuous"|"categorical"|"string">,
        "categories": <list(str)|None>,
        "role": <"feature"|"target"|"meta">
    }
    """
    data = Orange.data.Table(file_path)
    domain = data.domain

    domain_info = []

    # Parcourir les attributs (features)
    for feature in domain.attributes:
        domain_info.append({
            "name": feature.name,
            "type": ("continuous" if isinstance(feature, Orange.data.ContinuousVariable)
                     else "categorical" if isinstance(feature, Orange.data.DiscreteVariable)
            else "string"),
            "categories": feature.values if hasattr(feature, "values") else None,
            "role": "feature"
        })

    # Parcourir les cibles (targets)
    for target in domain.class_vars:
        domain_info.append({
            "name": target.name,
            "type": ("continuous" if isinstance(target, Orange.data.ContinuousVariable)
                     else "categorical" if isinstance(target, Orange.data.DiscreteVariable)
            else "string"),
            "categories": target.values if hasattr(target, "values") else None,
            "role": "target"
        })

    # Parcourir les métadonnées (meta)
    for meta_var in domain.metas:
        domain_info.append({
            "name": meta_var.name,
            "type": ("continuous" if isinstance(meta_var, Orange.data.ContinuousVariable)
                     else "categorical" if isinstance(meta_var, Orange.data.DiscreteVariable)
            else "string"),
            "categories": meta_var.values if hasattr(meta_var, "values") else None,
            "role": "meta"
        })
    print(domain_info)
    return domain_info


def domain_info_to_json(domain_info):
    """
    Convertit la liste de dictionnaires (issue de parse_tab_file_orange)
    en une chaîne JSON (str).
    """
    print(json.dumps(domain_info, ensure_ascii=False, indent=4))
    return json.dumps(domain_info, ensure_ascii=False, indent=4)


def compare_domain_info(domain_info1, domain_info2):
    """
    Compare deux listes de variables (domain_info1 et domain_info2).
    Vérifie que, pour chaque variable (même 'name'),
      le type, la liste de catégories, et le rôle sont identiques.
    Ignore l'ordre des variables.

    Retourne:
      - (True, "") si tout est identique
      - (False, "Message d'erreur") sinon
    """

    # Transformer domain_info2 en dict indexé par le name
    dict_info2 = {v["name"]: v for v in domain_info2}

    # 1) Vérifier que chaque variable de domain_info1 est dans domain_info2
    for var1 in domain_info1:
        name = var1["name"]
        if name not in dict_info2:
            return (False, f"La variable '{name}' est présente dans le premier JSON mais pas dans le second.")

        var2 = dict_info2[name]

        # Comparer le type
        if var1["type"] != var2["type"]:
            return (False, f"La variable '{name}' a un type différent: "
                           f"{var1['type']} vs {var2['type']}.")

        # Comparer le rôle
        if var1["role"] != var2["role"]:
            return (False, f"La variable '{name}' a un rôle différent: "
                           f"{var1['role']} vs {var2['role']}.")

        # Comparer les catégories (uniquement si type = 'categorical')
        if var1["type"] == "categorical":
            set1 = set(var1["categories"]) if var1["categories"] else set()
            set2 = set(var2["categories"]) if var2["categories"] else set()
            if set1 != set2:
                return (False, f"La variable '{name}' n'a pas les mêmes catégories.\n"
                               f"Fichier1={set1}\nFichier2={set2}")

    # 2) Vérifier qu'il n'y a pas de variables supplémentaires dans domain_info2
    dict_info1 = {v["name"]: v for v in domain_info1}
    for var_name in dict_info2:
        if var_name not in dict_info1:
            return (False, f"La variable '{var_name}' est présente dans le second JSON "
                           "mais pas dans le premier.")

    # Si on arrive ici, tout va bien

    return (True, "")


def compare_two_tab_files_as_json(file1, file2):
    """
    1) Lit deux fichiers .tab avec Orange,
    2) Les convertit en JSON,
    3) Compare les deux JSON (structure),
    4) Affiche un message final et renvoie True/False.
    """
    # 1) Récupérer la structure python
    domain_info_1 = parse_tab_file_orange(file1)
    domain_info_2 = parse_tab_file_orange(file2)

    # 2) Convertir en JSON
    json_str_1 = domain_info_to_json(domain_info_1)
    json_str_2 = domain_info_to_json(domain_info_2)

    # 3) Reconvertir le JSON en listes/dicos Python
    data1 = json.loads(json_str_1)
    data2 = json.loads(json_str_2)

    # Comparer
    ok, msg = compare_domain_info(data1, data2)

    if ok:
        print("✔ Les deux fichiers .tab (via JSON) correspondent parfaitement !")
        return True
    else:
        print("✖ Les deux fichiers .tab (via JSON) ne correspondent pas.")
        print("Raison :", msg)
        return False


# --------------------------------------------------------------------
# Exemple d'utilisation
# --------------------------------------------------------------------
# if __name__ == "__main__":
file1 = "C:/toto.tab"
file2 = "C:/totoo.tab"
# domain_info_1 = parse_tab_file_orange(file1)
# json_str_1 = domain_info_to_json(domain_info_1)
# data1 = json.loads(json_str_1)
#
# domain_info_2 = parse_tab_file_orange(file2)
# json_str_2 = domain_info_to_json(domain_info_2)
# data2 = json.loads(json_str_2)
compare_two_tab_files_as_json(file1, file2)