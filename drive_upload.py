from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

def upload_to_drive(filename):
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID .env dosyasında yok!")

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("token.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    else:
        try:
            gauth.Refresh()
        except:
            gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("token.json")

    drive = GoogleDrive(gauth)
    file = drive.CreateFile({'title': filename, 'parents':[{'id': folder_id}]})
    file.SetContentFile(filename)
    file.Upload()

    return file.get('webViewLink') or file.get('alternateLink')
