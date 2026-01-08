#!/usr/bin/env python3
# BTX Laudos — servidor local (proxy) para OpenAI
# Motivo: a chave da OpenAI NÃO deve ficar exposta no navegador e chamadas diretas do browser podem falhar por CORS.
# Referências: OpenAI API docs recomendam manter a API key no servidor. https://platform.openai.com/docs/api-reference/introduction

import os
import json
import time
from pathlib import Path
from typing import Any, Dict

import requests
from flask import Flask, request, jsonify, send_from_directory

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "web"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_DEFAULT = os.environ.get("OPENAI_MODEL", "gpt-5").strip()
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")

def _extract_output_text(resp: Dict[str, Any]) -> str:
    # Prefer the helper when present
    if isinstance(resp, dict) and resp.get("output_text"):
        return str(resp["output_text"])

    # Fallback: parse "output" array
    out = resp.get("output", [])
    texts = []
    if isinstance(out, list):
        for item in out:
            content = item.get("content")
            if isinstance(content, list):
                for c in content:
                    if c.get("type") in ("output_text", "text") and c.get("text"):
                        texts.append(c["text"])
    return "\n".join(texts).strip()

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.get("/health")
def health():
    return jsonify(ok=True, ts=int(time.time()))

@app.post("/api/ai")
def ai():
    if not OPENAI_API_KEY:
        return jsonify(error="OPENAI_API_KEY não configurada. Defina a variável de ambiente e reinicie o servidor."), 400

    payload = request.get_json(force=True, silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    model = (payload.get("model") or OPENAI_MODEL_DEFAULT).strip() or OPENAI_MODEL_DEFAULT

    if not prompt:
        return jsonify(error="Prompt vazio."), 400

    # Segurança: limite simples para evitar travar o PC com prompts enormes
    if len(prompt) > 60_000:
        return jsonify(error="Prompt muito grande. Reduza o texto ou divida em partes."), 400

    url = f"{OPENAI_BASE_URL}/v1/responses"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model,
        "instructions": "Você é um assistente clínico que APOIA A ESCRITA. Não diagnostique, não interprete imagens, não invente dados. Se faltar informação, diga o que falta. Escreva em português.",
        "input": prompt,
    }

    try:
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
        if r.status_code >= 400:
            return jsonify(error=f"OpenAI erro {r.status_code}", details=r.text[:2000]), 502

        resp = r.json()
        answer = _extract_output_text(resp) or ""
        return jsonify(answer=answer)

    except requests.RequestException as e:
        return jsonify(error="Falha ao chamar OpenAI", details=str(e)), 502

# Servir arquivos estáticos (PWA)
@app.get("/<path:path>")
def static_proxy(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == "__main__":
    # https://localhost é "secure context" para PWA em muitos navegadores; localhost também.
    # Rode:  python server.py
    port = int(os.environ.get("PORT", "5173"))
    app.run(host="127.0.0.1", port=port, debug=True)
