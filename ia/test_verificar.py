#!/usr/bin/env python3
"""Pruebas de ia/verificar.py. Correr: python3 -m unittest discover -s ia -p 'test_*.py'"""
import re
import unittest

import verificar as v


class Secretos(unittest.TestCase):
    def detecta(self, texto: str) -> bool:
        return any(re.search(p, texto) for p in v.SECRETOS)

    def test_detecta(self):
        for texto in ("-----BEGIN RSA PRIVATE KEY-----", "sk-" + "a" * 30, "ghp_" + "A1" * 18,
                      "auth_token=" + "ab12" * 6, "GAME900101HDFRRL09"):
            self.assertTrue(self.detecta(texto), texto)

    def test_no_marca_texto_normal(self):
        for texto in ("El token de la API se pide a Emi.", "commit 660cd7407c5726ec8d3aef27c32e1377b1c7e480",
                      "https://x.com/emilianomilla_/status/1234567890123456789", "password: nunca se guarda aquí"):
            self.assertFalse(self.detecta(texto), texto)

    def test_edad_de_pesos(self):
        texto, dias = v.edad_pesos()
        self.assertIsInstance(dias, int)
        self.assertIn("extraídos el", texto)


if __name__ == "__main__":
    unittest.main()
