from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import json
import tempfile

load_dotenv(dotenv_path=".env")

def upload_to_drive(filename):
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID .env dosyasında yok!")

    service_json = os.getenv("GOOGLE_SERVICE_JSON")
    if not service_json:
        raise ValueError("GOOGLE_SERVICE_JSON bulunamadı!")

    service_info = json.loads(service_json)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(service_info, f)
        temp_path = f.name

    try:
        gauth = GoogleAuth()
        scope = ['https://www.googleapis.com/auth/drive.file']
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(temp_path, scope)
        
        drive = GoogleDrive(gauth)
        file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
        file.SetContentFile(filename)
        file.Upload()
        
        return file.get('webViewLink') or file.get('alternateLink')
    finally:
        os.unlink(temp_path)
