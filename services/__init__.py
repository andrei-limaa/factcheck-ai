"""Utilitários HTTP que não expõem exceções com credenciais."""
from dataclasses import dataclass, field
from urllib.parse import urlsplit
import requests

@dataclass
class ResultadoBusca:
    itens: list[dict] = field(default_factory=list)
    aviso: str = ""

def texto(valor):
    return valor[:2500].strip() if isinstance(valor, str) else ""

def url_valida(valor):
    if not isinstance(valor, str) or any(c.isspace() for c in valor):
        return False
    try:
        p = urlsplit(valor)
        return p.scheme in {"http", "https"} and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False

def consultar(url, nome, **kwargs):
    try:
        r = requests.get(url, timeout=(5, 20), **kwargs)
        r.raise_for_status()
        dados = r.json()
        if not isinstance(dados, dict):
            raise ValueError
        return dados, ""
    except requests.Timeout:
        return {}, f"{nome}: tempo de espera excedido."
    except requests.HTTPError as erro:
        status = erro.response.status_code if erro.response is not None else "desconhecido"
        return {}, f"{nome}: erro HTTP {status}. Confira chave, cota e permissões."
    except requests.RequestException:
        return {}, f"{nome}: falha de conexão."
    except ValueError:
        return {}, f"{nome}: resposta inválida."
