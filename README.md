# FactCheck AI

O FactCheck AI é uma aplicação web para investigar notícias, manchetes e afirmações públicas. O usuário cola um texto e recebe um relatório em português baseado em evidências externas.

O projeto usa Flask, HTML e CSS, sem banco de dados ou autenticação. A interface apresenta as fontes por origem e mantém os links originais para conferência.

## O que ele faz

1. Recebe uma notícia ou afirmação no formulário.
2. Usa Claude, pela API Messages da Anthropic, para identificar a afirmação central e gerar termos de pesquisa.
3. Busca notícias relacionadas na GNews.
4. Consulta o Google Fact Check Tools quando `FACTCHECK_API_KEY` existe.
5. Consulta a Tavily em fontes oficiais (`gov.br`, `bcb.gov.br`, `tse.jus.br` e `senado.leg.br`) quando `TAVILY_API_KEY` existe.
6. Combina os resultados, remove URLs duplicadas e identifica as evidências como `E1`, `E2` etc.
7. Pede ao Claude uma comparação de datas, entidades, contexto e avaliações.
8. Exibe classificação, justificativa, limitações e links originais.

Cada fonte informa sua origem, como `Notícia`, `Checagem` ou `Tavily · fonte oficial`. O modelo não cria URLs; a aplicação só exibe links devolvidos pelas APIs.

## Classificações

O relatório pode indicar `VERDADEIRO`, `FALSO`, `ENGANOSO` ou `NÃO VERIFICADO`.

`NÃO VERIFICADO` significa que as evidências encontradas não permitem uma conclusão segura. A tela alerta que a informação pode ter chance de ser falsa ou enganosa, mas ausência de fontes não é tratada como prova definitiva. A recomendação é abrir as fontes e conferir o contexto.

## Configuração

Preencha o `.env` existente ou use `.env.example` como referência:

```env
ANTHROPIC_API_KEY=
GNEWS_API_KEY=
FACTCHECK_API_KEY=
TAVILY_API_KEY=
ANTHROPIC_MODEL=claude-haiku-4-5
```

As duas primeiras chaves são obrigatórias. As outras são opcionais. As chaves são carregadas com `load_dotenv()` e `os.getenv()` e não aparecem na interface.

## Instalação e execução

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
```

Abra `http://127.0.0.1:5000` no navegador. Se o ambiente `venv` já existir, use `.\venv\Scripts\python.exe app.py`.

## Limitações

O sistema analisa títulos, resumos e avaliações retornados pelas APIs; não lê integralmente todos os artigos. Serviços externos possuem limites de cota e cobertura. A validação dos IDs garante que o relatório cite fontes recuperadas, mas não garante que a interpretação esteja correta. Abra os links antes de compartilhar a informação.

Timeouts, erros HTTP, respostas vazias e JSON inválido viram avisos legíveis. Sem evidências utilizáveis, o sistema retorna `NÃO VERIFICADO` sem classificação conclusiva.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Os testes usam respostas simuladas e não precisam de chaves reais.

## Documentação

- [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create)
- [GNews](https://docs.gnews.io/)
- [Google Fact Check Tools](https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search)
- [Tavily Python SDK](https://docs.tavily.com/sdk/python/quick-start)
