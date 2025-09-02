# pylint: disable=W0212
import unittest
from unittest.mock import MagicMock
from nsj_integracao_api_client.service.integrador import IntegradorService

class TestLogComparacaoObjetos(unittest.TestCase):
    def setUp(self):
        self.log = MagicMock()
        self.injector = MagicMock()
        self.integrador = IntegradorService(self.injector, self.log)
        self.integrador._log_integridade = MagicMock()
        self.integrador._color = lambda text, code, console: text

    def teste_comparacao_dicionarios(self):
        obj1 = {"a": 1, "b": 2}
        obj2 = {"a": 1, "b": 3}
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_comparacao_listas(self):
        obj1 = [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]
        obj2 = [{"id": 1, "value": "A"}, {"id": 2, "value": "C"}]
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_lista_vazia(self):
        obj1 = []
        obj2 = [{"id": 1, "value": "A"}]
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_lista_diferentes(self):
        obj1 = [{"id": 1, "value": "A"}]
        obj2 = [{"id": 1, "value": "A"},{"id": 2, "value": "A"}]
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_tipos_diferentes(self):
        obj1 = {"a": 1}
        obj2 = [{"id": 1, "value": "A"}]
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_estruturas_aninhadas(self):
        obj1 = {"a": [{"id": 1, "value": "A"}]}
        obj2 = {"a": [{"id": 1, "value": "B"}]}
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_estruturas_aninhadas_diferentes_a(self):
        obj1 = {"a": []}
        obj2 = {"a": [{"id": 1, "value": "B"}]}
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_estruturas_aninhadas_diferentes_b(self):
        obj1 = {"c":"c", "a": [{"id": 1, "value": "B"}]}
        obj2 = {"c":"c", "a": []}
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

    def teste_estruturas_aninhadas_diferentes_c(self):
        obj1 = {"c":"c1", "a": []}
        obj2 = {"c":"c2", "a": [{"id": 1}]}
        self.integrador._log_comparacao_objetos("test_id", obj1, obj2)
        self.integrador._log_integridade.assert_called()

if __name__ == "__main__":
    unittest.main()