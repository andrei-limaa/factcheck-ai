import os
from services import ResultadoBusca, consultar, texto, url_valida

def buscar_checagens(termos):
    chave = os.getenv("FACTCHECK_API_KEY", "").strip()
    if not chave:
        return ResultadoBusca(aviso="Google Fact Check: opcional desativado (sem chave).")
    dados, aviso = consultar("https://factchecktools.googleapis.com/v1alpha1/claims:search",
        "Google Fact Check", params={"query": termos[:200], "languageCode": "pt", "pageSize": 5, "key": chave})
    if aviso:
        return ResultadoBusca(aviso=aviso)
    claims = dados.get("claims", [])
    if not isinstance(claims, list):
        return ResultadoBusca(aviso="Google Fact Check: formato inválido.")
    itens = []
    for c in claims:
        if not isinstance(c, dict) or not isinstance(c.get("claimReview", []), list):
            continue
        for r in c.get("claimReview", []):
            if not isinstance(r, dict) or not url_valida(r.get("url")):
                continue
            fonte = r.get("publisher") or {}
            itens.append({"tipo": "Checagem", "titulo": texto(c.get("text")),
                "descricao": texto(r.get("textualRating")), "data": texto(r.get("reviewDate")),
                "fonte": texto(fonte.get("name")) if isinstance(fonte, dict) else "", "url": r["url"]})
            if len(itens) == 5:
                return ResultadoBusca(itens)
    return ResultadoBusca(itens, "" if itens else "Google Fact Check: nenhuma checagem utilizável encontrada.")
