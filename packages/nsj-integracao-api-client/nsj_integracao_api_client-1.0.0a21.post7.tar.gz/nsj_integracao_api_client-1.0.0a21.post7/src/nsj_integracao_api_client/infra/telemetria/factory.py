"""
Factory para inicialização e configuração do sistema de telemetria.

Este módulo implementa o padrão Factory para facilitar a inicialização
e configuração do sistema de telemetria.
"""

import logging
from typing import Optional, Dict, Any

from nsj_integracao_api_client.infra.telemetria.telemetria_service import TelemetriaService
from nsj_integracao_api_client.infra.telemetria.telemetria_client import TelemetriaClient, TelemetriaConfig
from nsj_integracao_api_client.infra.telemetria.config import obter_config_ambiente, validar_config


class TelemetriaFactory:
    """
    Factory para inicialização e configuração do sistema de telemetria.

    Fornece métodos estáticos para facilitar a inicialização e obtenção
    de instâncias do sistema de telemetria.
    """

    _servico: Optional[TelemetriaService] = None
    _logger = logging.getLogger(__name__)

    @classmethod
    def inicializar_sistema(
        cls,
        url_api: str,
        empresadetentora: str = None,
        cnpjdetentora: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> TelemetriaService:
        """
        Inicializa o sistema de telemetria com configuração completa.

        Args:
            url_api: URL da API de telemetria
            timeout: Timeout em segundos
            max_retries: Número máximo de retentativas

        Returns:
            Instância do serviço de telemetria
        """
        try:
            # Criar configuração do cliente
            config = TelemetriaConfig(
                url_api=url_api,
                timeout=timeout,
                max_retries=max_retries,

            )

            # Criar cliente
            client = TelemetriaClient(config)

            # Obter serviço singleton
            servico = TelemetriaService()

            # Inicializar serviço
            servico.inicializar(empresadetentora, cnpjdetentora, client)

            # Armazenar referência
            cls._servico = servico

            cls._logger.info(
                "Sistema de telemetria inicializado: %s",
                url_api
            )

            return servico

        except Exception as e:
            cls._logger.error("Erro ao inicializar sistema de telemetria: %s", str(e))
            raise

    @classmethod
    def inicializar_sistema_simples(cls) -> TelemetriaService:
        """
        Inicializa o sistema de telemetria com configuração simples.

        Returns:
            Instância do serviço de telemetria
        """
        # Obter configuração do ambiente
        config_ambiente = obter_config_ambiente()

        # Usar configuração do ambiente ou valores padrão
        url_api = config_ambiente.url_api
        timeout = config_ambiente.timeout
        max_retries = config_ambiente.max_retries

        return cls.inicializar_sistema(
            url_api=url_api,
            timeout=timeout,
            max_retries=max_retries,

        )

    @classmethod
    def obter_servico(cls) -> Optional[TelemetriaService]:
        """
        Obtém a instância do serviço de telemetria.

        Returns:
            Instância do serviço ou None se não inicializado
        """
        if cls._servico is None:
            cls._logger.warning("Serviço de telemetria não inicializado")
        return cls._servico

    @classmethod
    def verificar_status(cls) -> Dict[str, Any]:
        """
        Verifica o status do sistema de telemetria.

        Returns:
            Dicionário com informações de status
        """
        status = {
            "inicializado": cls._servico is not None,
            "cliente_configurado": False,
            "configuracao_valida": False
        }

        if cls._servico is not None:
            status["cliente_configurado"] = cls._servico._client is not None

            if cls._servico._client is not None:
                try:
                    config = cls._servico._client.config
                    status["configuracao_valida"] = validar_config(config)
                    status["url_api"] = config.url_api
                    status["timeout"] = config.timeout
                    status["max_retries"] = config.max_retries
                except Exception as e:
                    cls._logger.error("Erro ao verificar configuração: %s", str(e))

        return status

    @classmethod
    def limpar_sistema(cls) -> None:
        """Limpa o sistema de telemetria."""
        if cls._servico is not None and cls._servico._client is not None:
            # Fechar sessão HTTP se disponível
            if hasattr(cls._servico._client, 'session'):
                cls._servico._client.session.close()

        cls._servico = None
        cls._logger.info("Sistema de telemetria limpo")


def inicializar_telemetria(
        url_api: str,
        empresadetentora: str,
        cnpjdetentora: str,
        timeout: int = 30,
        max_retries: int = 3) -> TelemetriaService:
    """
    Função de conveniência para inicializar telemetria.

    Args:
        url_api: URL da API de telemetria
        timeout: Timeout em segundos
        max_retries: Número máximo de retentativas

    Returns:
        Instância do serviço de telemetria
    """
    return TelemetriaFactory.inicializar_sistema(
        url_api=url_api,
        empresadetentora=empresadetentora,
        cnpjdetentora=cnpjdetentora,
        timeout=timeout,
        max_retries=max_retries
    )


def obter_telemetria() -> Optional[TelemetriaService]:
    """
    Função de conveniência para obter o serviço de telemetria.

    Returns:
        Instância do serviço de telemetria ou None se não inicializado
    """
    return TelemetriaFactory.obter_servico()