import subprocess
import os
import sys

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.utils import SimpleDialogQt
else:
    from orangecontrib.AAIT.utils import SimpleDialogQt

def mac_shellcopy(src, dest):
    """
    Copie des fichiers sur macOS avec gestion des timeouts pour Google Drive.

    :param src: Chemin source (str ou liste de str)
    :param dest: Chemin de destination (str)
    :returns: True si succès, False sinon
    """
    import io
    from tqdm import tqdm

    BUFFER_SIZE = 10 * 1024 * 1024  # 10MB buffer

    if isinstance(src, str):
        src = [src]

    src = [os.path.abspath(s) for s in src]
    dest = os.path.abspath(dest)

    def copy_file_with_retries(source_path, dest_path, max_retries=3):
        if not os.path.exists(source_path):
            print(f"Erreur : fichier source introuvable : {source_path}")
            return False

        # Créer le dossier de destination
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Obtenir la taille du fichier
        try:
            file_size = os.path.getsize(source_path)
        except OSError:
            print(f"Impossible d'obtenir la taille du fichier : {source_path}")
            return False

        for attempt in range(max_retries):
            try:
                with open(source_path, 'rb') as source, \
                        open(dest_path, 'wb') as target, \
                        tqdm(total=file_size, unit='B', unit_scale=True,
                             desc=f"Copie de {os.path.basename(source_path)}") as pbar:

                    while True:
                        buf = source.read(BUFFER_SIZE)
                        if not buf:
                            break
                        target.write(buf)
                        pbar.update(len(buf))

                # Vérifier que la copie est complète
                if os.path.getsize(dest_path) == file_size:
                    return True
                else:
                    print(
                        f"Erreur : taille du fichier incorrecte après la copie, tentative {attempt + 1}/{max_retries}")
                    continue

            except IOError as e:
                if e.errno == 60:  # Operation timed out
                    print(f"Timeout lors de la copie, tentative {attempt + 1}/{max_retries}")
                    # Supprimer le fichier partiellement copié
                    try:
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                    except:
                        pass
                    if attempt < max_retries - 1:
                        continue
                print(f"Erreur lors de la copie : {e}")
                return False
            except Exception as e:
                print(f"Erreur inattendue : {e}")
                return False

        return False

    try:
        for s in src:
            filename = os.path.basename(s)
            destination_path = os.path.join(dest, filename)

            # Notification de début
            os.system(
                f'''osascript -e 'display notification "Début de la copie de {filename}" with title "Copie de fichier"' ''')

            success = copy_file_with_retries(s, destination_path)

            if not success:
                # Notification d'échec
                os.system(
                    f'''osascript -e 'display notification "Échec de la copie de {filename}" with title "Erreur de copie"' ''')
                return False

            # Notification de succès
            os.system(
                f'''osascript -e 'display notification "Copie terminée de {filename}" with title "Copie réussie"' ''')

        return True

    except Exception as e:
        print(f"Erreur globale : {e}")
        return False