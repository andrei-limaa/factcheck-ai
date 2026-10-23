import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests

import agent
from services import ResultadoBusca, consultar, url_valida
from services.factcheck import buscar_checagens
from services.gnews import buscar_noticias


FONTE = {"tipo": "Notícia", "titulo": "Exemplo", "descricao": "Resumo",
         "fonte": "Jornal", "data": "2026-10-22", "url": "https://example.org/noticia"}
PESQUISA = {"afirmacao": "Afirmação de teste", "termos": "afirmação teste"}


class ServicosTests(unittest.TestCase):
    @patch.dict(os.environ, {"FACTCHECK_API_KEY": ""})
    @patch("services.requests.get")
    def test_google_opcional_nao_faz_requisicao(self, get):
        self.assertEqual(buscar_checagens("teste").itens, [])
        get.assert_not_called()

    @patch("services.requests.get", side_effect=requests.Timeout("segredo"))
    def test_timeout_sem_detalhe_sensivel(self, get):
        dados, aviso = consultar("https://example.org", "Teste")
        self.assertEqual(dados, {})
        self.assertNotIn("segredo", aviso)

    @patch("services.requests.get")
    def test_http_erro_nao_expoe_url(self, get):
        resposta = requests.Response()
        resposta.status_code = 403
        get.return_value.raise_for_status.side_effect = requests.HTTPError(
            "https://example.org?key=segredo", response=resposta)
        self.assertIn("403", consultar("https://example.org", "Teste")[1])
        self.assertNotIn("segredo", consultar("https://example.org", "Teste")[1])

    @patch("services.requests.get")
    def test_json_invalido(self, get):
        get.return_value.json.side_effect = ValueError("segredo")
        self.assertIn("inválida", consultar("https://example.org", "Teste")[1])

    @patch.dict(os.environ, {"GNEWS_API_KEY": "teste"})
    @patch("services.gnews.consultar")
    def test_gnews_limita_e_descarta_urls_invalidas(self, consultar_mock):
        artigos = [{"title": "x", "url": "javascript:alert(1)"}]
        artigos += [{"title": "x", "url": f"https://example.org/{i}", "source": None} for i in range(8)]
        consultar_mock.return_value = ({"articles": artigos}, "")
        itens = buscar_noticias("teste").itens
        self.assertEqual(len(itens), 5)
        self.assertTrue(all(url_valida(i["url"]) for i in itens))

    @patch.dict(os.environ, {"FACTCHECK_API_KEY": "teste"})
    @patch("services.factcheck.consultar")
    def test_google_mapeia_avaliacao(self, consultar_mock):
        consultar_mock.return_value = ({"claims": [{"text": "Afirmação",
            "claimReview": [{"textualRating": "Falso", "publisher": {"name": "Verificador"},
                             "url": "https://example.org/checagem"}]}]}, "")
        item = buscar_checagens("teste").itens[0]
        self.assertEqual(item["descricao"], "Falso")
        self.assertEqual(item["fonte"], "Verificador")


@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "teste", "GNEWS_API_KEY": "teste"})
class AgenteTests(unittest.TestCase):
    def executar(self, fontes, analise=None):
        with patch("agent.anthropic.Anthropic"), patch("agent.pedir_json") as pedir, \
                patch("agent.buscar_noticias", return_value=ResultadoBusca(fontes)), \
                patch("agent.buscar_checagens", return_value=ResultadoBusca(aviso="Opcional desativado")):
            pedir.side_effect = [PESQUISA, analise]
            resultado = agent.verificar("Afirmação original")
            return resultado, pedir.call_count

    def analise(self, **alteracoes):
        return {"classificacao": "VERDADEIRO", "evidencia_suficiente": True,
                "evidencias_utilizadas": ["E1"], "justificativa": "Suporte E1",
                "limitacoes": "Apenas resumos", **alteracoes}

    def test_sem_fontes_nao_pede_classificacao(self):
        r, chamadas = self.executar([])
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")
        self.assertEqual(chamadas, 1)

    def test_id_inventado_rejeitado(self):
        r, _ = self.executar([FONTE], self.analise(evidencias_utilizadas=["E99"]))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")
        self.assertEqual(r["evidencias_utilizadas"], [])

    def test_sem_suporte_suficiente_nao_classifica(self):
        r, _ = self.executar([FONTE], self.analise(evidencia_suficiente=False))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")

    def test_sem_citacoes_nao_classifica(self):
        r, _ = self.executar([FONTE], self.analise(evidencias_utilizadas=[]))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")

    def test_link_gerado_pelo_modelo_rejeitado(self):
        r, _ = self.executar([FONTE], self.analise(justificativa="Veja https://inventada.example"))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")
        self.assertNotIn("inventada", r["justificativa"])

    def test_classificacao_em_formato_invalido(self):
        r, _ = self.executar([FONTE], self.analise(classificacao=[]))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")

    def test_id_inventado_no_texto_rejeitado(self):
        r, _ = self.executar([FONTE], self.analise(justificativa="Confirmado por E99"))
        self.assertEqual(r["classificacao"], "NÃO VERIFICADO")

    def test_fontes_duplicadas_e_resultado_valido(self):
        r, _ = self.executar([FONTE, FONTE], self.analise())
        self.assertEqual(r["classificacao"], "VERDADEIRO")
        self.assertEqual(len(r["fontes"]), 1)
        self.assertEqual(r["fontes"][0]["url"], FONTE["url"])

    def test_json_modelo_invalido(self):
        client = MagicMock()
        client.messages.create.return_value = SimpleNamespace(
            stop_reason="end_turn", content=[SimpleNamespace(type="text", text="não é JSON")])
        with self.assertRaises(agent.ErroAgente):
            agent.pedir_json(client, "sistema", {}, 100)

    def test_entrada_vazia(self):
        with self.assertRaises(agent.ErroAgente):
            agent.verificar("   ")


if __name__ == "__main__":
    unittest.main()
