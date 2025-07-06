import os
import shutil
import datetime
from pathlib import Path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from db.db import get_writable_db_path
from utils.path_utils import get_writable_path
from utils import config

gauth = None
BACK_UP_FOLDER = "LaChapitaManager_backups"

def make_backup():
    """
    Create a backup of the current database and upload it to Google Drive if configured.
    :return: True if backup was successful, False otherwise.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"lachapita_backup_{timestamp}.db"
    db_path = get_writable_db_path()

    if config.backup_drive:
        # Name of the file with timestamp
        backup_file_path = os.path.join(get_writable_path(), backup_filename)
        try:
            shutil.copy(db_path, backup_file_path)
            upload_backup_to_drive(backup_file_path)
            Path.unlink(Path(backup_file_path))  # Remove the local backup file after uploading
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    else:
        # If not using Google Drive, just copy the database to the backup file
        try:
            make_local_backup(db_path, backup_filename)
        except Exception as e:
            print(f"Error creating local backup: {e}")
            return False
    return True

def format_files(files):
    """
    Format the list of files to include only the necessary information.
    :return: List of dictionaries with date, time, title, and id.
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
                    'id': file.get('id', None)  # Use get to avoid KeyError if 'id' is not present
                })
            except ValueError:
                continue  # Skip files with invalid timestamps
    return formatted_files

# ---------- LOCAL BACKUPS ----------

def make_local_backup(db_path, backup_filename):
    """
    Create a local backup of the database only if the last backup is older than a week.
    :param db_path: Path to the current database file.
    :param backup_file_path: Path where the backup will be saved.
    :param timestamp: Timestamp for the backup file name.
    :return: True if backup was successful, False otherwise.
    """

    try:
        folder_backups = os.path.join(get_writable_path(), BACK_UP_FOLDER)
        os.makedirs(folder_backups, exist_ok=True)
        backup_file_path = os.path.join(folder_backups, backup_filename)
    except Exception as e:
        print(f"Error creating backup folder: {e}")
        return False

    # Check if the last backup is older than a week
    existing_files = [{'title': f} for f in os.listdir(folder_backups) if f.startswith("lachapita_backup_") and f.endswith(".db")]
    formatted_files = format_files(existing_files)

    if formatted_files:
        # check the last backup date
        last_file = formatted_files[0]
        last_backup_date = datetime.datetime.combine(last_file['date'], last_file['time'])
        if (datetime.datetime.now() - last_backup_date) < datetime.timedelta(days=7):
            print("Last backup is less than a week old. Skipping local backup.")
            return False
        # Delete if more than 30 files
        if len(formatted_files) >= 29:
            for file in formatted_files[29:]:
                file_path = os.path.join(folder_backups, file['title'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted old backup: {file['title']}")

    try:
        shutil.copy(db_path, backup_file_path)
        print(f"Backup created successfully at {backup_file_path}")
        return True
    except Exception as e:
        print(f"Error creating local backup: {e}")
        return False

def get_backups_local():
    """
    Get a list of local backups from the backups folder.
    :return: List of dictionaries with date, time, title, and path.
    """
    folder_backups = os.path.join(get_writable_path(), BACK_UP_FOLDER)
    if not os.path.exists(folder_backups):
        return []

    existing_files = [{'title': f} for f in os.listdir(folder_backups) if f.startswith("lachapita_backup_") and f.endswith(".db")]
    formatted_files = format_files(existing_files)

    return formatted_files

def restore_backup_local(backup_filename):
    """
    Restore a local backup by copying it to the writable database path.
    :param backup_filename: Name of the backup file to restore.
    :return: True if restoration was successful, False otherwise.
    """
    folder_backups = os.path.join(get_writable_path(), BACK_UP_FOLDER)
    backup_file_path = os.path.join(folder_backups, backup_filename)

    if not os.path.exists(backup_file_path):
        print(f"Backup file {backup_filename} does not exist.")
        return False

    db_path = get_writable_db_path()
    try:
        shutil.copy(backup_file_path, db_path)
        print(f"Backup {backup_filename} restored successfully.")
        return True
    except Exception as e:
        print(f"Error restoring backup: {e}")
        return False

# ---------- GOOGLE DRIVE BACKUPS ----------

def upload_backup_to_drive(back_up_path):
    """
    Upload a backup file to Google Drive only if the last backup is older than a week.
    :param back_up_path: Path to the backup file to upload.
    :return: Tuple (bool, str) indicating success and the name of the uploaded file.
    """
    existing_files, folder_id, drive = get_backups_drive()

    if existing_files: last_file = existing_files[0]
    else: last_file = None

    if last_file:
        # Check if the last backup is from the last week
        date = last_file['date']
        time = last_file['time']
        last_backup_date = datetime.datetime.combine(date, time)
        if (datetime.datetime.now() - last_backup_date) < datetime.timedelta(days=7):
            return False, None

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
    Sets backup_drive to False if the client secrets file is not found.
    :return: True if authentication was successful, False otherwise.
    """
    global gauth
    print("Authenticating Google Drive...")
    client_secrets_path = os.path.join(get_writable_path(), "client_secrets.json")
    credentials_path = os.path.join(get_writable_path(), "mycredential.txt")
    print(f"client_secrets_path: {client_secrets_path}")
    print(f"credentials_path: {credentials_path}")
    if not os.path.exists(client_secrets_path):
        return False, f"client_secrets.json file not found. Please download it from the Google Developer Console and place it in {get_writable_path()}."

    try:
        gauth = GoogleAuth()
        gauth.settings['client_config_file'] = client_secrets_path

        gauth.LoadCredentialsFile(credentials_path)

        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile(credentials_path)
        return True, None
    except Exception as e:
        return False, f"Error authenticating with Google Drive: {e}"

def get_backups_drive():
    """
    Get a list of backups from the local backups folder.
    :return: Tuple (list of backups, folder_id, drive instance)
    """
    global gauth
    if gauth is None:
        authenticate_drive()

    drive = GoogleDrive(gauth)

    # Look for the backup folder in Google Drive
    folder_id = None

    file_list = drive.ListFile(
        {'q': f"title='{BACK_UP_FOLDER}' and mimeType='application/vnd.google-apps.folder'"}).GetList()

    if file_list:
        folder_id = file_list[0]['id']
    else:
        # Create the folder if it doesn't exist
        folder_drive = drive.CreateFile({'title': BACK_UP_FOLDER, 'mimeType': 'application/vnd.google-apps.folder'})
        folder_drive.Upload()
        folder_id = folder_drive['id']

    # Get list of backups in the folder
    query = f"'{folder_id}' in parents and trashed=false and title contains 'lachapita_backup_'"
    existing_files = drive.ListFile({'q': query}).GetList()

    existing_files.sort(key=lambda f: f['createdDate'], reverse=True)
    existing_files = format_files(existing_files)

    return existing_files, folder_id, drive

def restore_backup_drive(file_id):
    """
    Restore a backup from the google drive backups folder.
    """

    global gauth
    if gauth is None:
        authenticate_drive()

    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'id': file_id})
    db_path = get_writable_db_path()

    file.GetContentFile(db_path)
