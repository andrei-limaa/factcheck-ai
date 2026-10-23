import unittest
from app import app

class InterfaceTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_pagina_inicial(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Verificador de fatos", resposta.text)

    def test_entrada_vazia(self):
        resposta = self.client.post("/", data={"entrada": ""})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Insira uma notícia", resposta.text)
