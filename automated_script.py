import ftplib
import os
import time
import shutil
import xml.etree.ElementTree as ET
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

FTP_SERVER = 'localhost'
FTP_USER = 'nybsys'
FTP_PASS = '12345'
FTP_DIR = '/'

TEMP_FOLDER = 'temp'
LOCAL_FOLDER = 'local'
TRASH_FOLDER = 'trash'

# Ensure the folders exist
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(LOCAL_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

def download_files():
    ftp = ftplib.FTP()
    ftp.connect(FTP_SERVER, 21)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(FTP_DIR)
    
    filenames = ftp.nlst()
    for filename in filenames:
        local_temp_path = os.path.join(TEMP_FOLDER, filename)
        with open(local_temp_path, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
        local_final_path = os.path.join(LOCAL_FOLDER, filename)
        shutil.move(local_temp_path, local_final_path)

    ftp.quit()

class XMLFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.xml'):
            process_xml(event.src_path)

def process_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    data = {child.tag: child.text for child in root}
    print(data)
    move_to_trash(filepath)

def move_to_trash(filepath):
    shutil.move(filepath, os.path.join(TRASH_FOLDER, os.path.basename(filepath)))

event_handler = XMLFileHandler()
observer = Observer()
observer.schedule(event_handler, LOCAL_FOLDER, recursive=False)
observer.start()

try:
    while True:
        download_files()
        time.sleep(10)  # Check every 10 seconds for new files
except KeyboardInterrupt:
    observer.stop()
observer.join()
