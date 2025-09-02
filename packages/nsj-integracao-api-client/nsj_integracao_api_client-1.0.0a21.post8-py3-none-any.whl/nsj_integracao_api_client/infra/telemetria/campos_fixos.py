"""
Geração de campos fixos para eventos de telemetria.

Este módulo é responsável por gerar os campos fixos que são incluídos
em todos os eventos de telemetria, como informações da máquina, usuário,
aplicação e ambiente.
"""

import uuid
import socket
import os
from datetime import datetime
from typing import Dict, Any


def _obter_ip_maquina() -> str:
    """
    Obtém o IP da máquina atual.

    Returns:
        IP da máquina como string
    """
    try:
        # Conectar a um servidor externo para obter o IP público
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            # Fallback para hostname local
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def _obter_nome_maquina() -> str:
    """
    Obtém o nome da máquina atual.

    Returns:
        Nome da máquina como string
    """
    try:
        return socket.gethostname()
    except Exception:
        return "UNKNOWN"


def _obter_usuario() -> str:
    """
    Obtém o nome do usuário atual.

    Returns:
        Nome do usuário como string
    """
    return os.getenv('bd_user', None)


def _obter_servidor_sql() -> str:
    """
    Obtém o nome do servidor SQL atual.

    Returns:
        Nome do servidor SQL como string
    """
    return f"{os.getenv('bd_host', None)}@{os.getenv('bd_nome', None)}"


def obter_campos_fixos_padrao() -> Dict[str, Any]:
    """
    Obtém os campos fixos padrão da telemetria.

    Returns:
        Dicionário com os campos fixos padrão
    """
    return {
        "id": str(uuid.uuid4()),
        "datahoracliente": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sistema": "Integrador",
        "aplicativo": "nsj_integracao_api_client",
        "versaoaplicativo": None,
        "ip": _obter_ip_maquina(),
        "maquinausuario": _obter_nome_maquina(),
        "usuario": _obter_usuario(),
        "servidorsql": _obter_servidor_sql()
    }


def obter_campos_fixos(
        empresa_detentora: str = None,
        cnpj_detentora: str = None,
        empresa_sql: str = None,
        cnpj_empresa: str = None
    ) -> Dict[str, Any]:
    """
    Obtém os campos fixos para telemetria.

    Args:
        tenant: ID do tenant (opcional)
        empresa_detentora: Código da empresa detentora
        cnpj_detentora: CNPJ da empresa detentora
        empresa_sql: Código da empresa SQL
        cnpj_empresa: CNPJ da empresa

    Returns:
        Dicionário com os campos fixos
    """
    campos_base = obter_campos_fixos_padrao()

    campos = {
        **campos_base,
        "empresadetentora": empresa_detentora,
        "cnpjdetentora": cnpj_detentora,
        "empresasql": empresa_sql,
        "cnpjempresa": cnpj_empresa
    }
    return campos