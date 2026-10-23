"""Busca web da Tavily restrita a domínios oficiais."""
import os
from services import ResultadoBusca, texto, url_valida

def buscar_tavily(afirmacao):
    chave = os.getenv("TAVILY_API_KEY", "").strip()
    if not chave:
        return ResultadoBusca(aviso="Tavily: configure TAVILY_API_KEY para ativar a busca web oficial.")
    try:
        from tavily import TavilyClient
        resultado = TavilyClient(api_key=chave).search(query=afirmacao[:600], search_depth="basic", max_results=5,
            include_domains=["gov.br", "bcb.gov.br", "tse.jus.br", "senado.leg.br"])
        itens = []
        for item in resultado.get("results", []) if isinstance(resultado, dict) else []:
            if not isinstance(item, dict) or not url_valida(item.get("url")): continue
            url = item["url"]
            itens.append({"tipo": "Tavily · fonte oficial", "titulo": texto(item.get("title")),
                "descricao": texto(item.get("content")), "fonte": url.split("/")[2],
                "data": texto(item.get("published_date")), "url": url})
        return ResultadoBusca(itens, "" if itens else "Tavily: nenhuma fonte oficial encontrada.")
    except Exception:
        return ResultadoBusca(aviso="Tavily: não foi possível consultar a busca web.")
