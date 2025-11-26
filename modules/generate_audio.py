import os, json, asyncio, argparse
import edge_tts

# Módulo de Áudio usando Edge-TTS totalmente gratuito (Vozes do TikTok/Microsoft)

def load_config(path="config.yaml"):
    import yaml
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

cfg = load_config()
OUT_DIR = cfg.get("video",{}).get("audio_dir", "outputs/audio")

# Vozes sugeridas: 
# 'pt-BR-AntonioNeural' (Masculina - muito usada em shorts)
# 'pt-BR-FranciscaNeural' (Feminina - muito natural)
VOICE = "pt-BR-AntonioNeural"

async def generate_audio_async(text, output_file):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_file)

def generate_audio_from_script(script_path):
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {script_path}")

    with open(script_path, 'r', encoding='utf-8') as f:
        s = json.load(f)

    text = s.get('narracao')
    if not text:
        text = s.get('response', '') # fallback para JSON sujo
    
    # limpeza básica se o texto vier com JSON sujo
    if text and "{" in text:
        import re
        m = re.search(r'"narracao":\s*"([^"]+)"', text)
        if m: text = m.group(1)

    if not text or len(text) < 2:
        print(" [ERRO] Texto vazio. Não há nada para narrar.")
        return None

    print(f" -> Gerando áudio com Edge-TTS ({VOICE})...")
    
    os.makedirs(OUT_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    output_path = os.path.join(OUT_DIR, f"{base_name}.mp3")

    try:
        # Roda a função assíncrona do Edge TTS
        asyncio.run(generate_audio_async(text, output_path))
        print(f" -> Áudio salvo em: {output_path}")
        return output_path
    except Exception as e:
        print(f" [ERRO] Falha ao gerar áudio: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", "-s", required=True)
    args = parser.parse_args()
    
    generate_audio_from_script(args.script)