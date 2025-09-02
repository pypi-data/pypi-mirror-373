"""
Módulo de telemetria para o integrador de API.

Este módulo fornece funcionalidades para captura e envio de eventos de telemetria
durante a execução das operações de integração.
"""

from .telemetria_service import TelemetriaService
from .telemetria_client import TelemetriaClient
from .telemetria_decorator import telemetria, telemetria_simples
from .telemetria_metrics import TelemetriaMetrics, obter_metricas
from .factory import TelemetriaFactory, inicializar_telemetria, obter_telemetria
from .campos_fixos import obter_campos_fixos, obter_campos_fixos_padrao, obter_campos_fixos_para_tenant
from .config import obter_config_ambiente, obter_config_padrao, validar_config

__all__ = [
    # Serviços principais
    'TelemetriaService',
    'TelemetriaClient',
    'TelemetriaMetrics',

    # Decorators
    'telemetria',
    'telemetria_simples',

    # Factory e inicialização
    'TelemetriaFactory',
    'inicializar_telemetria',
    'obter_telemetria',

    # Métricas
    'obter_metricas',

    # Configuração
    'obter_campos_fixos',
    'obter_campos_fixos_padrao',
    'obter_campos_fixos_para_tenant',
    'obter_config_ambiente',
    'obter_config_padrao',
    'validar_config'
]