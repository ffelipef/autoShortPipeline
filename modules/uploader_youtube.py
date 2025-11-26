import os
import yaml
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) 
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_authenticated_service():
    cfg = load_config()
    youtube_cfg = cfg.get('youtube', {})
    
    secret_filename = youtube_cfg.get('client_secrets_file', 'client_secret.json')
    token_filename = youtube_cfg.get('credentials_file', 'token.json') # Usa o nome que está no seu config
    
    client_secrets_file = os.path.join(PROJECT_ROOT, secret_filename)
    token_path = os.path.join(PROJECT_ROOT, token_filename)

    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(f"Arquivo de segredos não encontrado em: {client_secrets_file}\nBaixe o JSON do Google Cloud e renomeie para {secret_filename}.")

    creds = None

    # tenta carregar o token salvo (yt-credentials.json)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # se não tiver token ou ele expirou, faz o login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # salva o novo token com o nome definido no config
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, category_id="22", privacy_status="private"):
    # garante caminho absoluto
    if not os.path.isabs(file_path):
        file_path = os.path.join(PROJECT_ROOT, file_path)

    if not os.path.exists(file_path):
        print(f"Erro: Arquivo de vídeo não encontrado em {file_path}")
        return None

    youtube = get_authenticated_service()
    
    print(f"Iniciando upload de: {os.path.basename(file_path)}...")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Enviando... {int(status.progress() * 100)}%")

    print("Upload Concluído com Sucesso!")
    return response

# Teste direto
if __name__ == "__main__":
    # ta p pegar um video especifico mas ele pega o video q foi criado (funciona só não é dinamico)
    test_video = "outputs/videos/1764037300_050598_shorts.mp4"
    
    # se o vídeo específico não existir mais o script vai avisar
    # se existir, vai tentar subir como PRIVADO
    try:
        upload_video(
            file_path=test_video, 
            title="Teste AutoShort Pipeline", 
            description="Upload automático via Python"
        )
    except Exception as e:
        print(f"Ocorreu um erro: {e}")