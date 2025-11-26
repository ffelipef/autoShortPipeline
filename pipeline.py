import os
import time
import sys

from modules.generate_script import generate_script_ollama, save_script
from modules.generate_images import generate_images_for_script
from modules.generate_audio import generate_audio_from_script
from modules.assemble_video import assemble_video

from modules.uploader_youtube import upload_video, load_config

def run_once(theme="história boba sobre comida", upload=False):
    print(f"--- Iniciando Pipeline: {theme} ---")
    
    # 1. Gerar Roteiro
    script = generate_script_ollama(theme)
    script_path = save_script(script)
    
    # 2. Gerar Imagens
    imgs = generate_images_for_script(script_path)
    
    # 3. Gerar Áudio
    audio_path = generate_audio_from_script(script_path)
    
    # 4. Montar Vídeo
    video_path = assemble_video(script_path, imgs, audio_path)
    print(f"✅ Vídeo gerado com sucesso: {video_path}")
    
    # 5. Upload
    if upload:
        cfg = load_config()
        if cfg.get("youtube", {}).get("enabled", False):
            print("Iniciando upload para o YouTube...")
            
            titulo = script.get("titulo", "Olha essa história Engraçada 👀")

            tags_do_script = " ".join(script.get("hashtags", []))
            hashtags = f"{tags_do_script} #funny #viral #cute"

            descricao = f"Gerado automaticamente por AutoShortPipeline.\n\n{hashtags}"
            
            try:
                upload_video(
                    file_path=video_path, 
                    title=titulo, 
                    description=descricao
                )
            except Exception as e:
                print(f"❌ Erro no upload: {e}")
        else:
            print("⚠️ Upload pulado: 'enabled' é false no config.yaml")
            
    return video_path

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    tema_arg = sys.argv[2] if len(sys.argv) > 2 else "curiosidade aleatória"
    
    for i in range(n):
        run_once(tema_arg, upload=True) 
        time.sleep(5)