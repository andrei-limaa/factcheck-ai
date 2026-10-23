import os
from services import ResultadoBusca, consultar, texto, url_valida

def buscar_noticias(termos):
    chave = os.getenv("GNEWS_API_KEY", "").strip()
    if not chave:
        return ResultadoBusca(aviso="GNews: chave não configurada.")
    dados, aviso = consultar("https://gnews.io/api/v4/search", "GNews",
        headers={"X-Api-Key": chave},
        params={"q": termos[:200], "lang": "pt", "max": 5, "sortby": "relevance"})
    if aviso:
        return ResultadoBusca(aviso=aviso)
    artigos = dados.get("articles", [])
    if not isinstance(artigos, list):
        return ResultadoBusca(aviso="GNews: formato inválido.")
    itens = []
    for a in artigos:
        if not isinstance(a, dict) or not url_valida(a.get("url")):
            continue
        fonte = a.get("source") or {}
        itens.append({"tipo": "Notícia", "titulo": texto(a.get("title")),
            "descricao": texto(a.get("description")), "data": texto(a.get("publishedAt")),
            "fonte": texto(fonte.get("name")) if isinstance(fonte, dict) else "",
            "url": a["url"]})
        if len(itens) == 5:
            break
    return ResultadoBusca(itens, "" if itens else "GNews: nenhuma notícia utilizável encontrada.")
