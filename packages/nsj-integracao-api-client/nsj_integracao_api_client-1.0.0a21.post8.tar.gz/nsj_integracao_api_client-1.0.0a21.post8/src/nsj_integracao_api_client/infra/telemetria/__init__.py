"""
Pacote de Telemetria - Versão Simplificada

Este pacote implementa um sistema de telemetria básico com 8 eventos essenciais:
- Carga Inicial (3 eventos): ITG_INI_CARGA, ITG_CARGA_ENTIDADE, ITG_FIM_CARGA
- Integração Contínua (3 eventos): ITG_INI_INTEG, ITG_INTEG_ENTIDADE, ITG_FIM_INTEG
- Verificação de Integridade (2 eventos): ITG_INI_VERIF, ITG_FIM_VERIF
"""

from nsj_integracao_api_client.infra.telemetria.telemetria_service import TelemetriaService
from nsj_integracao_api_client.infra.telemetria.telemetria_client import TelemetriaClient
from nsj_integracao_api_client.infra.telemetria.telemetria_decorator import telemetria, telemetria_simples
from nsj_integracao_api_client.infra.telemetria.telemetria_metrics import TelemetriaMetrics, obter_metricas
from nsj_integracao_api_client.infra.telemetria.factory import TelemetriaFactory, inicializar_telemetria, obter_telemetria
from nsj_integracao_api_client.infra.telemetria.campos_fixos import obter_campos_fixos
from nsj_integracao_api_client.infra.telemetria.config import obter_config_ambiente, validar_config

__all__ = [
    # Serviços principais
    'TelemetriaService',
    'TelemetriaClient',
    'TelemetriaMetrics',

    # Decoradores
    'telemetria',
    'telemetria_simples',

    # Factory e inicialização
    'TelemetriaFactory',
    'inicializar_telemetria',
    'obter_telemetria',

    # Métricas
    'obter_metricas',

    # Campos fixos
    'obter_campos_fixos',

    # Configuração
    'obter_config_ambiente',
    'validar_config'
]
