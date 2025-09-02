"""
Configuração da telemetria.

Este módulo define as configurações padrão e de ambiente para o sistema
de telemetria.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from .telemetria_client import TelemetriaConfig


@dataclass
class TelemetriaEnvironmentConfig:
    """Configuração de ambiente para telemetria."""

    # Configurações da API
    api_url: str = "http://telemetria.nasajon.com.br/api/events"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

    # Configurações de funcionalidade
    enable_telemetria: bool = True
    enable_metrics: bool = True
    enable_decorators: bool = True

    # Configurações de logging
    log_level: str = "INFO"
    log_telemetria_errors: bool = True

    # Configurações de performance
    max_metricas_cache: int = 1000
    cleanup_interval_seconds: int = 300


def obter_config_ambiente() -> TelemetriaEnvironmentConfig:
    """
    Obtém a configuração de ambiente para telemetria.

    Returns:
        Configuração de ambiente
    """
    config = TelemetriaEnvironmentConfig()

    # Sobrescreve com variáveis de ambiente se existirem
    if os.getenv("TELEMETRIA_API_URL"):
        config.api_url = os.getenv("TELEMETRIA_API_URL")

    if os.getenv("TELEMETRIA_TIMEOUT"):
        try:
            config.timeout = int(os.getenv("TELEMETRIA_TIMEOUT"))
        except ValueError:
            pass

    if os.getenv("TELEMETRIA_MAX_RETRIES"):
        try:
            config.max_retries = int(os.getenv("TELEMETRIA_MAX_RETRIES"))
        except ValueError:
            pass

    if os.getenv("TELEMETRIA_ENABLE"):
        config.enable_telemetria = os.getenv("TELEMETRIA_ENABLE").lower() in ("true", "1", "yes")

    if os.getenv("TELEMETRIA_ENABLE_METRICS"):
        config.enable_metrics = os.getenv("TELEMETRIA_ENABLE_METRICS").lower() in ("true", "1", "yes")

    if os.getenv("TELEMETRIA_ENABLE_DECORATORS"):
        config.enable_decorators = os.getenv("TELEMETRIA_ENABLE_DECORATORS").lower() in ("true", "1", "yes")

    if os.getenv("TELEMETRIA_LOG_LEVEL"):
        config.log_level = os.getenv("TELEMETRIA_LOG_LEVEL").upper()

    return config


def obter_config_cliente(config_ambiente: TelemetriaEnvironmentConfig) -> TelemetriaConfig:
    """
    Obtém a configuração do cliente de telemetria.

    Args:
        config_ambiente: Configuração de ambiente

    Returns:
        Configuração do cliente
    """
    return TelemetriaConfig(
        api_url=config_ambiente.api_url,
        timeout=config_ambiente.timeout,
        max_retries=config_ambiente.max_retries,
        retry_delay=config_ambiente.retry_delay,
        enable_telemetria=config_ambiente.enable_telemetria
    )


def obter_config_padrao() -> Dict[str, Any]:
    """
    Obtém a configuração padrão para telemetria.

    Returns:
        Dicionário com configuração padrão
    """
    return {
        "api_url": "http://telemetria.nasajon.com.br/api/events",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5,
        "enable_telemetria": True,
        "enable_metrics": True,
        "enable_decorators": True,
        "log_level": "INFO",
        "log_telemetria_errors": True,
        "max_metricas_cache": 1000,
        "cleanup_interval_seconds": 300
    }


def validar_config(config: TelemetriaEnvironmentConfig) -> bool:
    """
    Valida a configuração de telemetria.

    Args:
        config: Configuração a ser validada

    Returns:
        True se válida, False caso contrário
    """
    try:
        # Validações básicas
        if config.timeout <= 0:
            return False

        if config.max_retries < 0:
            return False

        if config.retry_delay < 0:
            return False

        if config.max_metricas_cache <= 0:
            return False

        if config.cleanup_interval_seconds <= 0:
            return False

        # Validações de URL
        if not config.api_url.startswith(("http://", "https://")):
            return False

        return True

    except Exception:
        return False