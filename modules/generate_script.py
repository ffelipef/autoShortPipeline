# modules/generate_script.py
import os, json, yaml, requests
from xml.parsers.expat import model
from typing import Dict, Any

# Este módulo usa Ollama (local) para gerar o JSON estruturado.
# Requer Ollama rodando localmente: https://ollama.com/docs

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


TEMPLATE_PROMPT = open("templates/story_template.txt","r",encoding="utf-8").read()


def generate_script_ollama(theme: str, scenes:int=3, cfg_path="config.yaml") -> Dict[str,Any]:
    cfg = load_config(cfg_path)
    host = cfg.get("ollama",{}).get("host","http://localhost:11434")
    model = cfg.get("ollama",{}).get("model","llama2")


    prompt = TEMPLATE_PROMPT + f"\nTema: {theme}\nCenas: {scenes}\n"
    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.9,
        "stream": False,
        "format": "json"
    }
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    text = r.text
    import re
    m = re.search(r"(\{[\s\S]*\})", text)
    if m:
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            # se json invalido, usar fallback
            lines = text.strip().split("\n")
            data = {
                "titulo": lines[0][:80] if lines else theme,
                "cenas": [],
                "narracao": " ".join(lines),
                "hashtags": ["#historia","#shorts"]
            }
    else:
        # fallback simples gerar cena com separadores
        lines = text.strip().split("\n")
        data = {
            "titulo": lines[0][:80] if lines else theme,
            "cenas": [],
            "narracao": " ".join(lines),
            "hashtags": ["#historia","#shorts"]
        }
    return data




def save_script(script: Dict[str,Any], out_dir="outputs/scripts") -> str:
    os.makedirs(out_dir, exist_ok=True)
    import time, uuid
    fname = f"{int(time.time())}_{uuid.uuid4().hex[:6]}.json"
    path = os.path.join(out_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    return path


if __name__ == "__main__":
    s = generate_script_ollama("história boba e engraçada", scenes=3)
    path = save_script(s)
    print("Salvo em:", path)