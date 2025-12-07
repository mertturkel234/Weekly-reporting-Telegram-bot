import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Google Drive servisine bağlan"""
    creds = None

    # token.json varsa yükle
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Token yükleme hatası: {e}")
            # Hatalı token'ı sil
            if os.path.exists('token.json'):
                os.remove('token.json')
            creds = None

    # Token yoksa veya geçersizse yeni al
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token yenileme hatası: {e}")
                # Yenilemede hata olursa token'ı sil ve yeni authentication yap
                if os.path.exists('token.json'):
                    os.remove('token.json')
                creds = None

        # Yeni authentication gerekli
        if not creds:
            client_json = os.getenv('GOOGLE_OAUTH_CLIENT_JSON')
            if not client_json:
                raise Exception("GOOGLE_OAUTH_CLIENT_JSON environment variable bulunamadı!")

            # JSON string'i dict'e çevir
            client_config = json.loads(client_json)

            # Flow oluştur
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        # Token'ı kaydet
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(filename):
    """Dosyayı Google Drive'a yükle"""
    try:
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not folder_id:
            raise Exception("GOOGLE_DRIVE_FOLDER_ID .env dosyasında yok!")

        service = get_drive_service()

        file_metadata = {
            'name': os.path.basename(filename),
            'parents': [folder_id]
        }

        media = MediaFileUpload(filename, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        print(f"✅ Dosya yüklendi: {file.get('webViewLink')}")
        return file.get('webViewLink')

    except Exception as e:
        print(f"❌ Drive upload hatası: {e}")
        raise e