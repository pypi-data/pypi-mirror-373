# Copier-colle qui utilise la fonction de Windows (pour avoir la fenêtre classique qui s'ouvre)

import os
import threading
import time
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.utils import SimpleDialogQt
else:
    from orangecontrib.AAIT.utils import SimpleDialogQt
if os.name=='nt':
    import os.path

    from win32com.shell import shell, shellcon
    import ctypes
    import ctypes.wintypes
    def win32_shellcopy(src, dest):
        """
        Copy files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :param dst: destination directory.
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        if not os.path.exists(src):
            SimpleDialogQt.BoxError("Error file not exist : "+src)
            return
        if isinstance(src, str):
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_COPY,
            src,
            os.path.abspath(dest),
            shellcon.FOF_NOCONFIRMMKDIR,  # flags
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            raise WindowsError('SHFileOperation failed: 0x%08x' % result)

        return not aborted

    def select_folder_ctypes():
        """
        Opens a native Windows folder selection dialog with enforced modal-like behavior, without attaching to any parent window.

        Features:
        - Uses the Windows Shell API (SHBrowseForFolder) to display the folder picker.
        - Detects and brings the folder selection window to the foreground immediately after opening.
        - Continuously forces the dialog window to stay topmost until a folder is selected or the dialog is closed.
        - Ensures Unicode support for folder paths (handles accents and special characters).
        - Properly frees allocated memory (PIDL) after selection.

        Note:
        - The dialog is not attached to any application window (no HWND owner is specified).

        Returns:
            str: The selected folder path, or an empty string if no selection was made.
        """
        BIF_RETURNONLYFSDIRS = 0x0001
        BIF_NEWDIALOGSTYLE = 0x0040
        MAX_PATH = 260

        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        HWND_TOPMOST = -1

        class BROWSEINFO(ctypes.Structure):
            _fields_ = [
                ("hwndOwner", ctypes.wintypes.HWND),
                ("pidlRoot", ctypes.c_void_p),
                ("pszDisplayName", ctypes.c_wchar_p),
                ("lpszTitle", ctypes.c_wchar_p),
                ("ulFlags", ctypes.wintypes.UINT),
                ("lpfn", ctypes.c_void_p),
                ("lParam", ctypes.c_void_p),
                ("iImage", ctypes.wintypes.INT),
            ]

        user32 = ctypes.windll.user32
        #kernel32 = ctypes.windll.kernel32
        shell32 = ctypes.windll.shell32

        SHBrowseForFolderW = shell32.SHBrowseForFolderW
        SHGetPathFromIDListW = shell32.SHGetPathFromIDListW
        CoTaskMemFree = ctypes.windll.ole32.CoTaskMemFree

        SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        SHGetPathFromIDListW.restype = ctypes.wintypes.BOOL

        SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFO)]
        SHBrowseForFolderW.restype = ctypes.c_void_p

        # Avant : liste des fenêtres existantes
        hwnd_list_before = []

        def enum_windows_proc(hwnd, lParam):
            hwnd_list_before.append(hwnd)
            return True

        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

        # Préparer browseinfo
        display_name_buffer = ctypes.create_unicode_buffer(MAX_PATH)

        browse_info = BROWSEINFO()
        browse_info.hwndOwner = 0
        browse_info.pidlRoot = None
        browse_info.pszDisplayName = ctypes.cast(display_name_buffer, ctypes.c_wchar_p)
        browse_info.lpszTitle = "Select a directory"
        browse_info.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
        browse_info.lpfn = None
        browse_info.lParam = None
        browse_info.iImage = 0

        # Ouvrir boîte de dialogue
        pidl = SHBrowseForFolderW(ctypes.byref(browse_info))

        # Petit délai pour affichage
        time.sleep(0.1)

        # Après ouverture : détecter la nouvelle fenêtre
        hwnd_list_after = []

        def enum_windows_proc_after(hwnd, lParam):
            hwnd_list_after.append(hwnd)
            return True

        EnumWindows(EnumWindowsProc(enum_windows_proc_after), 0)

        new_hwnds = list(set(hwnd_list_after) - set(hwnd_list_before))

        # Identifier la fenêtre de sélection
        selector_hwnd = None
        for hwnd in new_hwnds:
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                if "Select a directory" in title.value or "Browse For Folder" in title.value:
                    selector_hwnd = hwnd
                    break

        # 💥 Nouvelle partie : boucle qui surveille la fenêtre
        def enforce_modal(hwnd):
            if not hwnd:
                return
            while user32.IsWindow(hwnd):
                user32.SetForegroundWindow(hwnd)
                user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                time.sleep(0.2)  # Toutes les 200 ms on remet focus

        if selector_hwnd:
            threading.Thread(target=enforce_modal, args=(selector_hwnd,), daemon=True).start()

        # Lecture du résultat
        folder_path = ""

        if pidl:
            path_buffer = ctypes.create_unicode_buffer(MAX_PATH)
            success = SHGetPathFromIDListW(pidl, path_buffer)
            if success:
                folder_path = path_buffer.value
            else:
                folder_path=""

            CoTaskMemFree(ctypes.c_void_p(pidl))
        folder_path=folder_path.replace("\\","/")
        if folder_path:
            return folder_path
        else:
            return ""


    # Sélectionner un fichier image unique
    # path = select_file_ctypes(multi_select=False, file_filter="Images (*.jpg;*.png;*.jpeg)")
    #
    # # Sélectionner plusieurs fichiers Word
    # paths = select_file_ctypes(multi_select=True, file_filter="Word Documents (*.docx;*.doc)")
    import ctypes
    import ctypes.wintypes


    def select_file_ctypes(multi_select=False, file_filter="All Files (*.*)"):
        """
        Opens a native Windows file selection dialog with enforced modal-like behavior.

        Args:
            multi_select (bool): Allow selection of multiple files if True.
            file_filter (str): File type filters, e.g., "Images (*.jpg;*.png;*.jpeg)" or "Documents (*.docx;*.doc)".

        Returns:
            str: Selected file path(s) separated by ';', or an empty string if no selection was made.
        """
        OFN_ALLOWMULTISELECT = 0x00000200
        OFN_EXPLORER = 0x00080000
        OFN_FILEMUSTEXIST = 0x00001000
        MAX_PATH = 65536  # Large enough for multiple files

        class OPENFILENAME(ctypes.Structure):
            _fields_ = [
                ("lStructSize", ctypes.wintypes.DWORD),
                ("hwndOwner", ctypes.wintypes.HWND),
                ("hInstance", ctypes.wintypes.HINSTANCE),
                ("lpstrFilter", ctypes.c_wchar_p),
                ("lpstrCustomFilter", ctypes.c_wchar_p),
                ("nMaxCustFilter", ctypes.wintypes.DWORD),
                ("nFilterIndex", ctypes.wintypes.DWORD),
                ("lpstrFile", ctypes.c_wchar_p),
                ("nMaxFile", ctypes.wintypes.DWORD),
                ("lpstrFileTitle", ctypes.c_wchar_p),
                ("nMaxFileTitle", ctypes.wintypes.DWORD),
                ("lpstrInitialDir", ctypes.c_wchar_p),
                ("lpstrTitle", ctypes.c_wchar_p),
                ("Flags", ctypes.wintypes.DWORD),
                ("nFileOffset", ctypes.wintypes.WORD),
                ("nFileExtension", ctypes.wintypes.WORD),
                ("lpstrDefExt", ctypes.c_wchar_p),
                ("lCustData", ctypes.wintypes.LPARAM),
                ("lpfnHook", ctypes.c_void_p),
                ("lpTemplateName", ctypes.c_wchar_p),
                ("pvReserved", ctypes.c_void_p),
                ("dwReserved", ctypes.wintypes.DWORD),
                ("FlagsEx", ctypes.wintypes.DWORD),
            ]

        user32 = ctypes.windll.user32
        comdlg32 = ctypes.windll.comdlg32

        # Create filter string (must be null-separated and end with double null)
        if "(" in file_filter and ")" in file_filter:
            description = file_filter.split("(")[0].strip()
            pattern = file_filter[file_filter.find("(") + 1:file_filter.find(")")]
        else:
            description = "All Files"
            pattern = "*.*"
        filter_combined = f"{description}\0{pattern}\0All Files\0*.*\0\0"

        # Prepare buffer
        file_buffer = ctypes.create_unicode_buffer(MAX_PATH)

        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.hwndOwner = 0
        ofn.lpstrFilter = filter_combined
        ofn.lpstrFile = ctypes.cast(file_buffer, ctypes.c_wchar_p)
        ofn.nMaxFile = MAX_PATH
        ofn.lpstrTitle = "Select File(s)"
        ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST
        if multi_select:
            ofn.Flags |= OFN_ALLOWMULTISELECT

        # Avant ouvrir, mémoriser fenêtres existantes
        hwnd_list_before = []

        def enum_windows_proc(hwnd, lParam):
            hwnd_list_before.append(hwnd)
            return True

        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

        # Ouvre la boîte de sélection
        if not comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
            return ""  # Cancelled

        time.sleep(0.1)

        # Après ouverture
        hwnd_list_after = []
        EnumWindows(EnumWindowsProc(lambda hwnd, lParam: hwnd_list_after.append(hwnd) or True), 0)

        new_hwnds = list(set(hwnd_list_after) - set(hwnd_list_before))

        selector_hwnd = None
        for hwnd in new_hwnds:
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                if "Select" in title.value:
                    selector_hwnd = hwnd
                    break

        def enforce_modal(hwnd):
            if not hwnd:
                return
            while user32.IsWindow(hwnd):
                user32.SetForegroundWindow(hwnd)
                user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0,
                                    0x0002 | 0x0001 | 0x0040)  # SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
                time.sleep(0.2)

        if selector_hwnd:
            threading.Thread(target=enforce_modal, args=(selector_hwnd,), daemon=True).start()

        # Lecture du buffer brut
        buffer_content = ctypes.wstring_at(ctypes.addressof(file_buffer), file_buffer._length_)

        # Split sur \0
        parts = buffer_content.split('\0')
        parts = [p.replace("\\", "/") for p in parts if p]

        if multi_select:
            if len(parts) >= 2:
                folder = parts[0]
                files = parts[1:]
                full_paths = [f"{folder}/{file}" for file in files]
                return ';'.join(full_paths)
            elif len(parts) == 1:
                return parts[0]
            else:
                return ""
        else:
            return parts[0] if parts else ""




def select_new_file_ctypes(file_filter="All Files (*.*)"):
    """
    Opens a native Windows file dialog for creating a new file.

    Args:
        file_filter (str): File type filters, e.g., "Text Files (*.txt)" or "All Files (*.*)".

    Returns:
        str: Selected file path as a string, or an empty string if cancelled.
    """
    OFN_EXPLORER = 0x00080000
    MAX_PATH = 65536  # Large buffer for filename

    class OPENFILENAME(ctypes.Structure):
        _fields_ = [
            ("lStructSize", ctypes.wintypes.DWORD),
            ("hwndOwner", ctypes.wintypes.HWND),
            ("hInstance", ctypes.wintypes.HINSTANCE),
            ("lpstrFilter", ctypes.c_wchar_p),
            ("lpstrCustomFilter", ctypes.c_wchar_p),
            ("nMaxCustFilter", ctypes.wintypes.DWORD),
            ("nFilterIndex", ctypes.wintypes.DWORD),
            ("lpstrFile", ctypes.c_wchar_p),
            ("nMaxFile", ctypes.wintypes.DWORD),
            ("lpstrFileTitle", ctypes.c_wchar_p),
            ("nMaxFileTitle", ctypes.wintypes.DWORD),
            ("lpstrInitialDir", ctypes.c_wchar_p),
            ("lpstrTitle", ctypes.c_wchar_p),
            ("Flags", ctypes.wintypes.DWORD),
            ("nFileOffset", ctypes.wintypes.WORD),
            ("nFileExtension", ctypes.wintypes.WORD),
            ("lpstrDefExt", ctypes.c_wchar_p),
            ("lCustData", ctypes.wintypes.LPARAM),
            ("lpfnHook", ctypes.c_void_p),
            ("lpTemplateName", ctypes.c_wchar_p),
            ("pvReserved", ctypes.c_void_p),
            ("dwReserved", ctypes.wintypes.DWORD),
            ("FlagsEx", ctypes.wintypes.DWORD),
        ]

    user32 = ctypes.windll.user32
    comdlg32 = ctypes.windll.comdlg32

    # Convert file_filter into Windows format: "Description\0Pattern\0..."
    if "(" in file_filter and ")" in file_filter:
        description = file_filter.split("(")[0].strip()
        pattern = file_filter[file_filter.find("(")+1:file_filter.find(")")]
    else:
        description = "All Files"
        pattern = "*.*"

    # Extract first extension for default
    first_ext = pattern.split(";")[0].strip().lstrip("*.")
    if not first_ext:
        first_ext = "txt"

    filter_combined = f"{description}\0{pattern}\0All Files\0*.*\0\0"

    file_buffer = ctypes.create_unicode_buffer(MAX_PATH)

    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.hwndOwner = 0
    ofn.lpstrFilter = filter_combined
    ofn.lpstrFile = ctypes.cast(file_buffer, ctypes.c_wchar_p)
    ofn.nMaxFile = MAX_PATH
    ofn.lpstrTitle = "Create New File"
    ofn.Flags = OFN_EXPLORER
    ofn.lpstrDefExt = first_ext  # <- extension ajoutée automatiquement si absente

    # Mémoriser les fenêtres existantes
    hwnd_list_before = []
    def enum_windows_proc(hwnd, lParam):
        hwnd_list_before.append(hwnd)
        return True

    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

    # Ouvre la boîte de dialogue
    if not comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
        return ""

    time.sleep(0.1)

    # Fenêtres après
    hwnd_list_after = []
    EnumWindows(EnumWindowsProc(lambda hwnd, lParam: hwnd_list_after.append(hwnd) or True), 0)
    new_hwnds = list(set(hwnd_list_after) - set(hwnd_list_before))

    selector_hwnd = None
    for hwnd in new_hwnds:
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            title = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, title, length + 1)
            if "Save" in title.value:
                selector_hwnd = hwnd
                break

    def enforce_modal(hwnd):
        if not hwnd:
            return
        while user32.IsWindow(hwnd):
            user32.SetForegroundWindow(hwnd)
            user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0,
                                0x0002 | 0x0001 | 0x0040)  # SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            time.sleep(0.2)

    if selector_hwnd:
        threading.Thread(target=enforce_modal, args=(selector_hwnd,), daemon=True).start()

    result = ctypes.wstring_at(ctypes.addressof(file_buffer), file_buffer._length_)
    return result.split('\0', 1)[0].replace("\\", "/")



import subprocess
import os
import sys

def mac_shellcopy(src, dest):
    """
    Copy files or directories on macOS using AppleScript to show a native progress dialog.
    :param src: Path to source file or directory (str or list of str)
    :param dest: Path to destination directory (str)
    :returns: True if successful, False otherwise
    """
    if isinstance(src, str):
        src = [src]
    src = [os.path.abspath(s) for s in src]
    dest = os.path.abspath(dest)

    # AppleScript for copying with progress dialog
    script = f'''
    set srcList to {{{", ".join([f'POSIX file "{s}"' for s in src])}}}
    set destFolder to POSIX file "{dest}"
    tell application "Finder"
        repeat with aSrc in srcList
            duplicate aSrc to destFolder with replacing
        end repeat
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print("AppleScript error:", result.stderr)
            return False
    except Exception as e:
        print("Error:", e)
        return False

# Usage:
# mac_shellcopy("/path/to/source", "/path/to/destination")
