import os
import time
import hashlib

class DebugUtils:
    """
    Classe utilitária para operações de depuração.
    """

    @staticmethod
    def conditional_trace(condition, func, *args, **kwargs):
        """
        Avalia uma condição e executa uma função passada por parâmetro se a condição for verdadeira.

        Args:
            condition (bool): A condição a ser avaliada.
            func (callable): A função a ser executada se a condição for verdadeira.
            *args: Argumentos posicionais a serem passados para a função.
            **kwargs: Argumentos nomeados a serem passados para a função.
        """
        if condition:
            func(*args, **kwargs)


    @staticmethod
    def save_to_file(filename, content):
        """
        Salva o conteúdo fornecido em um arquivo.

        Args:
            filename (str): O caminho e nome do arquivo onde o conteúdo será salvo.
            content (str): O conteúdo a ser salvo no arquivo.
        """

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode, encoding="utf-8") as f:
            f.write(content + '\n')


    @staticmethod
    def hash():
        """
        Gera um hash SHA-256 baseado no horário atual.

        Retorna:
            str: Uma string hexadecimal representando o hash SHA-256 do horário atual.

        """
        return hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()

    @staticmethod
    def time():
        """
        Retorna o horário atual como uma string.

        Retorna:
            str: O horário atual em segundos desde a época.
        """
        return str(time.time())


_du = DebugUtils

# # Exemplo de uso do conditional_trace para salvar conteúdo em um arquivo
# DebugUtils.conditional_trace(
#     condition=True,
#     func=DebugUtils.save_to_file,
#     filename='/path/to/file.txt',
#     content='Este é um exemplo de conteúdo.'
# )
