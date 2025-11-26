import os, json, requests, time, random, re, unicodedata
from pathlib import Path
from urllib.parse import quote

# CONFIGURAÇÃO
def load_config(path="config.yaml"):
    import yaml
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

cfg = load_config()
OUT_DIR = cfg.get("video",{}).get("images_dir","outputs/images")

def remove_accents(input_str):
    #traduz acentos para nao dar problema na API
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_text_for_prompt(text: str) -> str:
    #remover
    if not text: return ""
    
    # 1. acentos (CRÍTICO PARA POLLINATIONS)
    text = remove_accents(text)
    
    # 2. estruturas de JSON e sujeira
    text = re.sub(r'[\[\]\{\}\"\']', '', text)
    text = re.sub(r'(titulo:|cenas:|texto:|narracao:|visual:|prompt:)', '', text, flags=re.IGNORECASE)
    
    # 3. pontuação solta no começo (ex: ", texto")
    text = text.lstrip(' ,.-')
    
    # 4. quebras de linha
    text = text.replace('\n', ' ').replace('\r', '').strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text[:200]

def generate_from_prompt(prompt: str, out_dir=None, index=0) -> str:
    if out_dir is None:
        out_dir = OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    # Limpeza total
    clean_prompt = clean_text_for_prompt(prompt)
    
    print(f"Gerando imagem {index}...")
    print(f"  -> Prompt original: {prompt[:30]}...")
    print(f"  -> Prompt limpo (ASCII): {clean_prompt[:30]}...")

    seed = random.randint(0, 999999)
    
    # ajudando o modelo(prompt em ingles)
    full_prompt = f"pixar style, 3d animation, vibrant colors, cute character, {clean_prompt}"
    
    encoded_prompt = quote(full_prompt)
    
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&seed={seed}&nologo=true&model=turbo"

    try:
        response = requests.get(url, timeout=200)
        
        if response.status_code >= 500:
            print("     [500] Erro no servidor. Tentando prompt simplificado...")
            simple_prompt = quote(f"cartoon 3d scene {index}")
            url = f"https://image.pollinations.ai/prompt/{simple_prompt}?width=720&height=1280&seed={seed}&nologo=true&model=turbo"
            response = requests.get(url, timeout=200)

        response.raise_for_status()
        
        data = response.content
        fname = Path(out_dir) / f"{int(time.time())}_{index}.jpg"
        
        with open(fname, 'wb') as f:
            f.write(data)
            
        print(f"  -> Sucesso! Salvo em: {fname}")
        return str(fname)

    except Exception as e:
        print(f"  [ERRO] Falha na imagem {index}: {e}")
        return None

def generate_images_for_script(script_path: str, out_dir=None):
    with open(script_path, 'r', encoding='utf-8') as f:
        s = json.load(f)

    cenas = s.get('cenas', [])
    
    if not cenas:
        print(" [AVISO] Cenas vazias. Extraindo do texto bruto...")
        raw_text = s.get('narracao') or s.get('response') or json.dumps(s)
        clean_text = clean_text_for_prompt(raw_text)
        frases = [f.strip() for f in clean_text.split('.') if len(f.strip()) > 10]
        
        if not frases:
            frases = ["Happy character scene", "Action scene 3d cartoon", "Funny ending scene"]
            
        for frase in frases[:5]:
            cenas.append({"visual": frase, "texto": frase})

    results = []
    print(f" -> Processando {len(cenas)} cenas com Pollinations (ASCII Mode)...")
    
    for i, c in enumerate(cenas):
        raw_prompt = c.get('visual') or c.get('texto') or "scene"
        
        img_path = generate_from_prompt(raw_prompt, out_dir=out_dir, index=i)
        results.append(img_path)
        
        time.sleep(2) # Pausa maior para evitar erro 429/500
    
    # Filtrar None (imagens que falharam)
    valid_results = [img for img in results if img is not None]
    if not valid_results:
        print(" [ERRO] Nenhuma imagem foi gerada com sucesso!")
        return []
    
    if len(valid_results) < len(results):
        print(f" [AVISO] {len(results) - len(valid_results)} imagem(ns) falharam. Continuando com {len(valid_results)} imagens.")
    
    return valid_results

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--script', '-s', required=True)
    parser.add_argument('--out-dir', '-o')
    args = parser.parse_args()

    if not os.path.exists(args.script):
        print("Script não encontrado.")
        sys.exit(1)

    try:
        imgs = generate_images_for_script(args.script, out_dir=args.out_dir)
        print("\n--- IMAGENS GERADAS COM SUCESSO ---")
        print(imgs)
    except Exception as e:
        print('Erro geral:', e)