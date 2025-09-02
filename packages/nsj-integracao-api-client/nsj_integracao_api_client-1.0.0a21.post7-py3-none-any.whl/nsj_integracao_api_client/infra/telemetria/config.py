"""
Configuração do sistema de telemetria.

Este módulo gerencia as configurações do sistema de telemetria,
permitindo configuração via environment variables e valores padrão.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetriaEnvironmentConfig:
    """Configuração do ambiente de telemetria."""

    url_api: str
    tenant: Optional[int] = None
    ambiente: str = "PROD"
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.3
    enable_telemetria: bool = True
    enable_metrics: bool = True
    enable_decorators: bool = True
    log_level: str = "INFO"
    empresa_detentora: str = None
    cnpj_detentora: str = None


def obter_config_ambiente() -> TelemetriaEnvironmentConfig:
    """
    Obtém a configuração do ambiente de telemetria.

    Returns:
        Configuração do ambiente
    """
    return TelemetriaEnvironmentConfig(
        url_api=os.getenv("TELEMETRIA_URL_API", "http://telemetria.nasajon.com.br/api/events"),
        tenant=int(os.getenv("TELEMETRIA_TENANT", "0")) if os.getenv("TELEMETRIA_TENANT") else None,
        ambiente=os.getenv("TELEMETRIA_AMBIENTE", "PROD"),
        timeout=int(os.getenv("TELEMETRIA_TIMEOUT", "30")),
        max_retries=int(os.getenv("TELEMETRIA_MAX_RETRIES", "3")),
        retry_backoff_factor=float(os.getenv("TELEMETRIA_RETRY_BACKOFF_FACTOR", "0.3")),
        enable_telemetria=os.getenv("TELEMETRIA_ENABLE", "true").lower() == "true",
        enable_metrics=os.getenv("TELEMETRIA_ENABLE_METRICS", "true").lower() == "true",
        enable_decorators=os.getenv("TELEMETRIA_ENABLE_DECORATORS", "true").lower() == "true",
        log_level=os.getenv("TELEMETRIA_LOG_LEVEL", "INFO"),
        empresa_detentora=os.getenv("TELEMETRIA_EMPRESA_DETENTORA", ""),
        cnpj_detentora=os.getenv("TELEMETRIA_CNPJ_DETENTORA", "")
    )


def obter_config_padrao() -> TelemetriaEnvironmentConfig:
    """
    Obtém a configuração padrão de telemetria.

    Returns:
        Configuração padrão
    """
    return TelemetriaEnvironmentConfig(
        url_api="http://telemetria.nasajon.com.br/api/events",
        tenant=None,
        ambiente="PROD",
        timeout=30,
        max_retries=3,
        retry_backoff_factor=0.3,
        enable_telemetria=True,
        enable_metrics=True,
        enable_decorators=True,
        log_level="INFO"
    )


def validar_config(config: TelemetriaEnvironmentConfig) -> bool:
    """
    Valida a configuração de telemetria.

    Args:
        config: Configuração a ser validada

    Returns:
        True se a configuração é válida, False caso contrário
    """
    try:
        # Validar URL da API
        if not config.url_api or not config.url_api.startswith(("http://", "https://")):
            return False

        # Validar timeout
        if config.timeout <= 0:
            return False

        # Validar max_retries
        if config.max_retries < 0:
            return False

        # Validar retry_backoff_factor
        if config.retry_backoff_factor < 0:
            return False

        # Validar tenant se fornecido
        if config.tenant is not None and config.tenant <= 0:
            return False

        # Validar ambiente
        if config.ambiente not in ["PROD", "QA", "DEV"]:
            return False

        # Validar log_level
        if config.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return False

        return True

    except Exception:
        return False


def obter_config_cliente(url_api: str, tenant: Optional[int] = None,
                        ambiente: str = "PROD", timeout: int = 30,
                        max_retries: int = 3) -> TelemetriaEnvironmentConfig:
    """
    Obtém configuração específica para um cliente.

    Args:
        url_api: URL da API de telemetria
        tenant: ID do tenant (opcional)
        ambiente: Ambiente de execução
        timeout: Timeout em segundos
        max_retries: Número máximo de retentativas

    Returns:
        Configuração do cliente
    """
    return TelemetriaEnvironmentConfig(
        url_api=url_api,
        tenant=tenant,
        ambiente=ambiente,
        timeout=timeout,
        max_retries=max_retries,
        retry_backoff_factor=0.3,
        enable_telemetria=True,
        enable_metrics=True,
        enable_decorators=True,
        log_level="INFO"
    )
