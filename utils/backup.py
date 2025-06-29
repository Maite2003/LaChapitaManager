import os
import shutil
import datetime
from pathlib import Path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from db.db import DB_PATH

gauth = None

def make_backup():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"lachapita_backup_{timestamp}.db"

    # Name of the file with timestamp
    try:
        shutil.copy(DB_PATH, backup_filename)
        upload_backup_to_drive(backup_filename)
        Path.unlink(Path(backup_filename))  # Remove the local backup file after uploading
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def delete_backup_google_drive(drive, folder_id):
    """Delete backups older than 15 days from Google Drive and backups from the last hour."""
    now = datetime.datetime.now()
    file_list = drive.ListFile({
        'q': f"'{folder_id}' in parents and trashed=false"
    }).GetList()

    for file in file_list:
        name = file['title']
        if name.startswith("lachapita_backup_") and name.endswith(".db"):
            try:
                timestamp_str = name.replace("lachapita_backup_", "").replace(".db", "")
                file_datetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

                # Delete if older than 15 days or within the last hour
                if (now - file_datetime > datetime.timedelta(days=15)) or \
                        (now - file_datetime < datetime.timedelta(hours=1)):
                    file.Delete()
                    print(f"Deleted Drive backup: {name}")
            except Exception as e:
                print(f"Skipping {name} in Drive: {e}")

def upload_backup_to_drive(back_up_path):

    existing_files, folder_id, drive = get_backups()

    if existing_files: last_file = existing_files[0]
    else: last_file = None

    if last_file:
        # Check if the last backup is from the last week
        date = last_file['date']
        time = last_file['time']
        last_backup_date = datetime.datetime.combine(date, time)
        if (datetime.datetime.now() - last_backup_date) < datetime.timedelta(days=7):
            return

    # Upload the new backup file
    file_name = os.path.basename(back_up_path)
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(back_up_path)
    file_drive.Upload()

    # Delete if more than 30 files
    if len(existing_files) >= 29:
        for file in existing_files[29:]:
            file.Delete()
            print(f"Deleted old backup from Drive: {file['title']}")

    return True, file_name

def authenticate_drive():
    """
    Authenticate with Google Drive and return the authenticated drive instance.
    """
    global gauth
    gauth = GoogleAuth()
    # Ruta absoluta del directorio donde está este archivo backup.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Desde utils/ subir un nivel y entrar a desktop/
    client_secrets_path = os.path.abspath(os.path.join(base_dir, "..", "desktop", "client_secrets.json"))
    gauth.settings['client_config_file'] = client_secrets_path

    gauth.LoadCredentialsFile("mycredential.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycredential.txt")

def get_backups():
    """
    Get a list of backups from the local backups folder.
    Returns a list of dictionaries with 'date' and 'time'.
    """
    global gauth
    if gauth is None:
        authenticate_drive()

    drive = GoogleDrive(gauth)

    # Look for the backup folder in Google Drive
    folder_name = "LaChapitaManager_backups"
    folder_id = None

    file_list = drive.ListFile(
        {'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"}).GetList()

    if file_list:
        folder_id = file_list[0]['id']
    else:
        # Create the folder if it doesn't exist
        folder_drive = drive.CreateFile({'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'})
        folder_drive.Upload()
        folder_id = folder_drive['id']

    # Get list of backups in the folder
    query = f"'{folder_id}' in parents and trashed=false and title contains 'lachapita_backup_'"
    existing_files = drive.ListFile({'q': query}).GetList()

    existing_files.sort(key=lambda f: f['createdDate'], reverse=True)
    existing_files = format_files(existing_files)

    return existing_files, folder_id, drive

def format_files(files):
    """
    Format the list of files to include only the necessary information.
    """
    formatted_files = []
    for file in files:
        if file['title'].startswith("lachapita_backup_") and file['title'].endswith(".db"):
            timestamp_str = file['title'].replace("lachapita_backup_", "").replace(".db", "")
            try:
                file_datetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                formatted_files.append({
                    'date': file_datetime.date(),
                    'time': file_datetime.time(),
                    'title': file['title'],
                    'id': file['id']
                })
            except ValueError:
                continue  # Skip files with invalid timestamps
    return formatted_files

def restore_backup(file_id):
    """
    Restore a backup from the google drive backups folder.
    """

    global gauth
    if gauth is None:
        authenticate_drive()

    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(DB_PATH)  # Downloads the file to local_filename.ext
