BTX Laudos — FINAL (V5) para COMPUTADOR (PWA + Memória)

✅ O que tem:
- Tela "Meus casos" (lista, busca, filtro, KPIs)
- Memória automática (IndexedDB) — salva sozinho ao digitar
- Status: Rascunho / Enviado / Finalizado
- Fotos com preview + legenda + ordenar/remover
- PDF com fotos e legendas
- IA por prompt (corrigir/padronizar/reescrever)
- Exportar/Importar caso (.json) para backup
- PWA (instalar no PC) + offline (service worker)

IMPORTANTE (PWA):
- PWA/Service Worker só funcionam em HTTPS (ou localhost).
- Abrir index.html direto no PC (file://) funciona como app, MAS sem instalar PWA e sem SW.
- Recomendado: GitHub Pages.

Como publicar no GitHub Pages (rápido):
1) Crie um repositório (ex.: btx-laudos-final)
2) Envie estes arquivos para a raiz:
   - index.html
   - manifest.webmanifest
   - service-worker.js
   - pasta icons/
3) Settings → Pages → Deploy from branch → main / root
4) Acesse o link do Pages no Chrome/Edge e clique em "Instalar".

Observação do PDF:
- jsPDF vem por CDN. Abra 1 vez com internet (no Pages) para cachear e depois fica offline.
