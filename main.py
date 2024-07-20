import eel
import pandas as pd
import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog
import xlrd 
import PyInstaller.config
import time
PyInstaller.config.CONF['distpath'] = "./VerzeichnisGenerator"

eel.init('web')

subdirs = []

@eel.expose
def select_folder():
    root = tk.Tk()
    root.withdraw()  
    root.attributes('-topmost', True)  
    folder_path = filedialog.askdirectory(parent=root)
    root.destroy()  
    return folder_path if folder_path else None

@eel.expose
def load_subdirs():
    global subdirs
    try:
        with open('subdirs.json', 'r') as f:
            subdirs = json.load(f)
    except FileNotFoundError:
        subdirs = []
    return subdirs

@eel.expose
def save_subdirs():
    with open('subdirs.json', 'w') as f:
        json.dump(subdirs, f)

@eel.expose
def add_subdir(new_subdir):
    global subdirs
    if new_subdir and new_subdir not in subdirs:
        subdirs.append(new_subdir)
        save_subdirs()
    return subdirs

@eel.expose
def remove_subdir(subdir):
    global subdirs
    if subdir in subdirs:
        subdirs.remove(subdir)
        save_subdirs()
    return subdirs

@eel.expose
def create_directories(file_data, file_name, output_dir, column_number):
    if not file_data or not output_dir:
        return {"success": False, "message": "Please provide both Excel file and output directory."}

    try:
        temp_file_path = os.path.join(os.path.dirname(__file__), "temp_" + file_name)
        with open(temp_file_path, "wb") as f:
            f.write(bytes(file_data))

        if file_name.endswith('.xls'):
            df = pd.read_excel(temp_file_path, engine='xlrd')
        else:
            df = pd.read_excel(temp_file_path)

        os.remove(temp_file_path)

        column_number = int(column_number) - 1  

        if column_number < 0 or column_number >= len(df.columns):
            return {"success": False, "message": "Invalid column number."}

        unique_strings = df.iloc[:, column_number].unique()
        create_folder_structure(unique_strings, output_dir, subdirs)
        return {"success": True, "message": "Ordner wurden kreiert!"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def create_folder_structure(unique_strings, output_dir, subdirs):
    for string in unique_strings:
        if pd.notna(string):
            clean_string = ''.join(c for c in str(string) if c.isalnum() or c in (' ', '_', '-'))
            clean_string = clean_string.strip()

            main_dir = os.path.normpath(os.path.join(output_dir, clean_string))
            try:
                os.makedirs(main_dir, exist_ok=True)
            except OSError as e:
                print(f"Error waehrend der erstellung von: {main_dir}: {e}")
                continue

            for subdir in subdirs:
                subdir_path = os.path.normpath(os.path.join(main_dir, subdir))
                try:
                    os.makedirs(subdir_path, exist_ok=True)
                except OSError as e:
                    print(f"Error waehrend der erstellung von: {subdir_path}: {e}")


def get_browser_path(browser_name):
    try:
        return subprocess.check_output(f'where {browser_name}', shell=True).decode().strip()
    except subprocess.CalledProcessError:
        return None

chrome_path = get_browser_path("chrome")
chromium_path = get_browser_path("chromium")

try:
    if chrome_path or chromium_path:
        eel.start('index.html', size=(300, 200))
    else:
        eel.start('index.html', size=(300, 200), mode="default")
except OSError as e:
    if "WinError 10048" in str(e):
        pass
