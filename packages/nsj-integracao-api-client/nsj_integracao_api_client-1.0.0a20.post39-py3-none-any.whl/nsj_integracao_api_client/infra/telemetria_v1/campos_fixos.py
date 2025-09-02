"""
Configuração dos campos fixos da telemetria.

Este módulo define os campos fixos que serão incluídos em todos os eventos
de telemetria, conforme especificação.
"""

import uuid
import socket
import getpass
import platform
from typing import Dict, Any
from datetime import datetime


def obter_campos_fixos(
    sistema: str = "Integrador",
    aplicativo: str = "nsj_integracao_api_client",
    versao_aplicativo: str = "2.1.0",
    tenant: int = 0,
    empresa_detentora: str = "",
    cnpj_detentora: str = "",
    empresa_sql: str = "",
    cnpj_empresa: str = "",
    servidor_sql: str = ""
) -> Dict[str, Any]:
    """
    Obtém os campos fixos para telemetria.

    Args:
        sistema: Nome do aplicativo
        aplicativo: Nome do exe
        versao_aplicativo: Versão do exe
        tenant: ID do tenant
        empresa_detentora: Código da empresa detentora
        cnpj_detentora: CNPJ da empresa dona do contrato
        empresa_sql: Código da empresa que gerou o evento
        cnpj_empresa: CNPJ da empresa que gerou o evento
        servidor_sql: Identificação do servidor no padrão host@nome_database

    Returns:
        Dicionário com os campos fixos
    """
    return {
        "id": str(uuid.uuid4()),
        "datahoracliente": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sistema": sistema,
        "aplicativo": aplicativo,
        "versaoaplicativo": versao_aplicativo,
        "tenant": tenant,
        "empresadetentora": empresa_detentora,
        "cnpjdetentora": cnpj_detentora,
        "empresasql": empresa_sql,
        "cnpjempresa": cnpj_empresa,
        "ip": _obter_ip_maquina(),
        "maquinausuario": _obter_nome_maquina(),
        "usuario": _obter_usuario(),
        "servidorsql": servidor_sql
    }


def _obter_ip_maquina() -> str:
    """
    Obtém o IP da máquina.

    Returns:
        IP da máquina ou string vazia se não conseguir obter
    """
    try:
        # Conecta a um endereço externo para descobrir o IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            # Fallback: obtém o hostname
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""


def _obter_nome_maquina() -> str:
    """
    Obtém o nome DNS da estação.

    Returns:
        Nome da máquina ou string vazia se não conseguir obter
    """
    try:
        return socket.gethostname()
    except Exception:
        return ""


def _obter_usuario() -> str:
    """
    Obtém o nome do usuário conectado na estação.

    Returns:
        Nome do usuário ou string vazia se não conseguir obter
    """
    try:
        return getpass.getuser()
    except Exception:
        return ""


def obter_campos_fixos_padrao() -> Dict[str, Any]:
    """
    Obtém os campos fixos com valores padrão.

    Returns:
        Dicionário com os campos fixos padrão
    """
    return obter_campos_fixos()


def obter_campos_fixos_para_tenant(
    tenant: int,
    empresa_detentora: str = "",
    cnpj_detentora: str = "",
    empresa_sql: str = "",
    cnpj_empresa: str = "",
    servidor_sql: str = ""
) -> Dict[str, Any]:
    """
    Obtém os campos fixos para um tenant específico.

    Args:
        tenant: ID do tenant
        empresa_detentora: Código da empresa detentora
        cnpj_detentora: CNPJ da empresa dona do contrato
        empresa_sql: Código da empresa que gerou o evento
        cnpj_empresa: CNPJ da empresa que gerou o evento
        servidor_sql: Identificação do servidor no padrão host@nome_database

    Returns:
        Dicionário com os campos fixos para o tenant
    """
    return obter_campos_fixos(
        tenant=tenant,
        empresa_detentora=empresa_detentora,
        cnpj_detentora=cnpj_detentora,
        empresa_sql=empresa_sql,
        cnpj_empresa=cnpj_empresa,
        servidor_sql=servidor_sql
    )