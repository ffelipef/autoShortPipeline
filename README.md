# 🎬 AutoShort Pipeline

AutoShort Pipeline é uma ferramenta de automação escrita em Python que gera vídeos curtos (Shorts/Reels/TikToks) do zero usando Inteligência Artificial Local e faz o upload automaticamente para o YouTube.

---

O projeto utiliza Ollama para roteiros, Pollinations para imagens, Edge-TTS para narração natural e MoviePy para edição.

---

## ✨ Funcionalidades
🧠 Roteiros com IA Local: Gera scripts virais usando Llama3 (ou outro modelo) via Ollama.

🎨 Imagens Automáticas: Cria visuais baseados no contexto de cada cena.

🗣️ Narração Natural: Usa a tecnologia Edge-TTS (vozes neurais da Microsoft) sem custos.

✂️ Edição Automática: Monta o vídeo, redimensiona imagens para 9:16, sincroniza áudio e adiciona legendas.

🚀 Upload Automático: Envia o vídeo finalizado diretamente para seu canal do YouTube com título, descrição e tags.

---

## 🛠️ Pré-requisitos
Antes de começar, certifique-se de ter instalado:

1. Python 3.10+.

2. Ollama (com o modelo llama3 baixado: ollama pull llama3).

3.  FFMPEG (Essencial para o MoviePy processar vídeos).

---

## 📦 Instalação
Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/AutoShortPipeline.git
cd AutoShortPipeline
```

Crie e ative um ambiente virtual (Recomendado):
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração
1. Configurações Gerais (config.yaml)
Renomeie o arquivo config.example.yaml para config.yaml na raiz do projeto e ajuste conforme necessário:

YAML

ollama:
  model: "llama3" # ou mistral, gemma2, etc.

youtube:
  enabled: true
  client_secrets_file: "client_secret.json"
  credentials_file: "yt-credentials.json"
2. Credenciais do YouTube
Para que o upload funcione, você precisa criar um projeto no Google Cloud:

1. Acesse o Google Cloud Console.

2. Ative a YouTube Data API v3.

3. Crie credenciais de OAuth 2.0 Client ID (Desktop App).

4. Baixe o JSON, renomeie para client_secret.json e coloque na pasta raiz do projeto.

5. Adicione seu e-mail como "Test User" na tela de consentimento OAuth.

---

## 🚀 Como Usar
Certifique-se de que o Ollama está rodando em segundo plano.

Abra o terminal na pasta do projeto e rode:

```bash
# Sintaxe: python pipeline.py [QTD_VIDEOS] "TEMA DO VIDEO"

python pipeline.py 1 "Curiosidades sobre gatos"
```
O script irá:

1. Gerar o roteiro.

2. Criar as imagens e áudio na pasta outputs/.

3. Renderizar o vídeo MP4.

4. Abrir o navegador para autenticar e fazer o upload.

---

## 📂 Estrutura do Projeto
AutoShortPipeline/
├── modules/               # Scripts principais (audio, video, script, upload)
├── outputs/               # Onde os arquivos gerados são salvos (ignorado pelo git)
├── assets/                # Músicas de fundo ou templates
├── config.yaml            # Suas configurações (NÃO SOBE PRO GITHUB)
├── client_secret.json     # Sua chave do Google (NÃO SOBE PRO GITHUB)
├── pipeline.py            # Arquivo principal para rodar
└── requirements.txt       # Lista de bibliotecas

---

## 🛡️ Aviso Legal
Este projeto utiliza APIs e modelos de terceiros. Certifique-se de respeitar os termos de serviço do YouTube, OpenAI (se usar), e Pollinations. O conteúdo gerado é responsabilidade do usuário.

Feito com 🐍 Python.