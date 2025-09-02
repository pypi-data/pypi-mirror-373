import os
import time
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import getTempDir
else:
    from orangecontrib.AAIT.utils.MetManagement import getTempDir
"""
only windows!!!
when you launch GPT4all without an interface it is not possible to simply close it, this file is intended to stop it 
when it has not been used for a long time (1hour)

"""


def exit_chat_exe():
    """
    send a command line to stop gpt4all process
    """
    ldc = '"taskkill /im chat.exe /t /f"'
    try:
        os.system(ldc)
    except Exception as e:
        print(e)
        print(e)


def need_to_quit(delta_time_in_second):
    """
    read a file in temp folder. this file contains the date and time of the last call to GPT4ALL
    if it has been too long since the last call was made, the process is stopped
    """
    # Obtenir le chemin du répertoire temp de Windows
    temp_dir = getTempDir()

    # Créer le nom complet du fichier
    file_path = os.path.join(temp_dir, 'date_heure.txt')

    try:
        with open(file_path, 'r') as file:
            stored_time_seconds = int(file.read())

        current_time_seconds = int(time.time())
        time_difference = abs(current_time_seconds - stored_time_seconds)
        print(f"Temps écoulé depuis la dernière écriture : {time_difference} secondes")
        if time_difference < delta_time_in_second:
            return False
    except FileNotFoundError:
        print("File date_heure.txt not found")

        ## si le fichier n'existe pas on quitte pour éviter la fermeture si l'utisateur veut se servir de 4all
        return True
    return True


if os.name != 'nt':
    print("only windows -> exiting")
    exit(0)

print("debut attente")
time.sleep(30)
while True:
    # si horodatage non mis à jour au bout 1h on kill and quit
    if need_to_quit(3600) == True:
        print("need to quit")
        exit_chat_exe()
        exit(0)
    time.sleep(10)
print("fin attente")
