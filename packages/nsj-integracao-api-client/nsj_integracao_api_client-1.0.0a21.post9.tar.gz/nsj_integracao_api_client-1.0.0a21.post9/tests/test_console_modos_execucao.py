# pylint: disable=W0212
import unittest
from unittest.mock import MagicMock

from argparse import Namespace
import os

class TestConsoleModosExecucao(unittest.TestCase):
    def setUp(self):
        pass

    def teste_iniciar_console_interativo(self):
        os.environ["ONLY_CONSOLE"] = "True"
        params = Namespace(
            modo_interativo=True,
            command=None
        )
        from nsj_integracao_api_client.client_console import ClientConsole
        console = ClientConsole()
        console.modo_interativo = MagicMock()
        console.main(params)
        console.modo_interativo.assert_called()

    def teste_iniciar_modo_console(self):
        os.environ["ONLY_CONSOLE"] = "True"
        params = Namespace(
            modo_interativo=False,
            command="integrar"
        )
        from nsj_integracao_api_client.client_console import ClientConsole
        console = ClientConsole()
        console.executar_comando = MagicMock()
        console.main(params)
        console.executar_comando.assert_called()

    def teste_iniciar_modo_ui(self):
        os.environ["ONLY_CONSOLE"] = "True"
        params = Namespace(
            modo_interativo=False,
            command=None
        )
        from nsj_integracao_api_client.client_console import ClientConsole
        console = ClientConsole()
        console.modo_janela = MagicMock()
        console.main(params)
        console.modo_janela.assert_called()

    def teste_iniciar_modo_ui_console_erro(self):
        os.environ["ONLY_CONSOLE"] = "True"
        params = Namespace(
            modo_interativo=False,
            command=None
        )
        from nsj_integracao_api_client.client_console import ClientConsole
        console = ClientConsole()
        with self.assertRaises(Exception) as context:
            console.main(params)
        self.assertEqual(str(context.exception), "Modo janela desabilitado.")


if __name__ == "__main__":
    unittest.main()