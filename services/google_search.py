"""Busca web oficial do Google Custom Search JSON API."""
import os
from services import ResultadoBusca, consultar, texto, url_valida

def buscar_google(termos):
    chave, cx = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip(), os.getenv("GOOGLE_SEARCH_CX", "").strip()
    if not chave or not cx:
        return ResultadoBusca(aviso="Google Web: configure GOOGLE_SEARCH_API_KEY e GOOGLE_SEARCH_CX para ativar.")
    dados, aviso = consultar("https://www.googleapis.com/customsearch/v1", "Google Web",
        params={"key": chave, "cx": cx, "q": termos[:200], "num": 5, "hl": "pt-BR"})
    if aviso: return ResultadoBusca(aviso=aviso)
    itens = []
    for item in dados.get("items", []):
        if not isinstance(item, dict) or not url_valida(item.get("link")): continue
        itens.append({"tipo": "Google Web", "titulo": texto(item.get("title")),
                      "descricao": texto(item.get("snippet")), "fonte": texto(item.get("displayLink")),
                      "data": "", "url": item["link"]})
        if len(itens) == 5: break
    return ResultadoBusca(itens, "" if itens else "Google Web: nenhum resultado utilizável encontrado.")
