import os, json, yaml
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.config import change_settings
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip

def load_config(path="config.yaml"):
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
        
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

cfg = load_config()
W, H = cfg.get('video',{}).get('resolution', [1080, 1920]) 
FPS = cfg.get('video',{}).get('fps', 24)
VIDEO_DIR = cfg.get("video",{}).get("output_dir", "outputs/videos")

#função de juntar imagens e áudio em vídeo final
def assemble_video(script_path, images, audio_path):
    print(f" -> Iniciando montagem do vídeo: {os.path.basename(script_path)}")

    # 1. calidações iniciais
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")
    
    if not images:
        raise ValueError("A lista de imagens está vazia!")

    # 2. Carregar cenas do script para legendas
    cenas = []
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cenas = data.get('cenas', [])
    except Exception as e:
        print(f" [AVISO] Não foi possível ler as cenas para legendas: {e}")

    if len(cenas) < len(images):
        cenas.extend([{"texto": ""} for _ in range(len(images) - len(cenas))])

    # 3. Calcular Tempos
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration + 0.1 #margem de segurança (tire se quiser, nao recomendo)
    dur_per_scene = total_duration / len(images)
    
    print(f" -> Áudio: {total_duration:.2f}s | Imagens: {len(images)} | Tempo por cena: {dur_per_scene:.2f}s")

    # 4. Criar Clipes
    final_clips = []
    for i, (img_path, cena_data) in enumerate(zip(images, cenas)):
        if not os.path.exists(img_path):
            print(f" [PULANDO] Imagem não existe: {img_path}")
            continue

        img_clip = ImageClip(img_path).set_duration(dur_per_scene)
        
        img_ratio = img_clip.w / img_clip.h
        target_ratio = W / H
        
        #crop centralizado para preencher 9:16
        if img_ratio > target_ratio:
            img_clip = img_clip.resize(height=H)
            img_clip = img_clip.crop(x1=img_clip.w/2 - W/2, width=W)
        else:
            img_clip = img_clip.resize(width=W)
            img_clip = img_clip.crop(y1=img_clip.h/2 - H/2, height=H)

        # logica de legenda com ImageMagick
        texto = cena_data.get('texto', '')
        if texto and len(texto) > 3:
            try:
                txt_clip = TextClip(
                    texto, fontsize=55, color='white', font='Arial', 
                    stroke_color='black', stroke_width=3, method='caption', 
                    size=(W-80, None), align='center'
                ).set_duration(dur_per_scene).set_position(('center', 0.70), relative=True)
                
                img_clip = CompositeVideoClip([img_clip, txt_clip]).set_duration(dur_per_scene)
            except Exception:
                pass

        final_clips.append(img_clip)

    # 5. Juntar Vídeo e Áudio
    print(" -> Renderizando vídeo final...")
    video_final = concatenate_videoclips(final_clips, method="compose")
    video_final = video_final.set_audio(audio_clip)

    # Preparar saída
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Root do projeto
    output_dir = os.path.join(base_dir, "outputs", "videos")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.basename(script_path).replace(".json", "_shorts.mp4")
    out_path = os.path.join(output_dir, filename)

    try:
        video_final.write_videofile(
            out_path, 
            fps=FPS, 
            codec='libx264', 
            audio_codec='libmp3lame',#melhor q aac
            temp_audiofile='temp-audio.mp3', 
            remove_temp=True, 
            preset='ultrafast',
            threads=4
        )
        print(f"\n--- VÍDEO PRONTO: {out_path} ---")
        
    except Exception as e:
        print(f"\n[ERRO NA RENDERIZAÇÃO PADRÃO]: {e}")
        # fallback sem logger se der erro de barra de progresso
        if "ext" in str(e) or "logger" in str(e):
            print(" -> Tentando novamente sem barra de progresso (logger=None)...")
            video_final.write_videofile(
                out_path, fps=FPS, codec='libx264', audio_codec='libmp3lame',
                temp_audiofile='temp-audio.mp3', remove_temp=True, preset='ultrafast',
                logger=None
            )
            
    return out_path