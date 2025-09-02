"""
Factory para inicialização do sistema de telemetria.

Este módulo fornece funções para inicializar e configurar o sistema
de telemetria de forma padronizada.
"""

import logging
from typing import Optional, Dict, Any
from .config import obter_config_ambiente, obter_config_cliente, validar_config
from .campos_fixos import obter_campos_fixos_para_tenant
from .telemetria_service import TelemetriaService


class TelemetriaFactory:
    """
    Factory para criação e configuração do sistema de telemetria.

    Responsável por inicializar todos os componentes necessários
    e configurar o sistema de acordo com as configurações de ambiente.
    """

    @staticmethod
    def inicializar_sistema(
        tenant: int,
        empresa_detentora: str = "",
        cnpj_detentora: str = "",
        empresa_sql: str = "",
        cnpj_empresa: str = "",
        servidor_sql: str = "",
        logger: Optional[logging.Logger] = None
    ) -> Optional[TelemetriaService]:
        """
        Inicializa o sistema de telemetria.

        Args:
            tenant: ID do tenant
            empresa_detentora: Código da empresa detentora
            cnpj_detentora: CNPJ da empresa dona do contrato
            empresa_sql: Código da empresa que gerou o evento
            cnpj_empresa: CNPJ da empresa que gerou o evento
            servidor_sql: Identificação do servidor no padrão host@nome_database
            logger: Logger para registro de erros

        Returns:
            Instância do serviço de telemetria ou None se falhar
        """
        try:
            # Obtém configuração de ambiente
            config_ambiente = obter_config_ambiente()

            # Valida configuração
            if not validar_config(config_ambiente):
                if logger:
                    logger.error("Configuração de telemetria inválida")
                return None

            # Verifica se telemetria está habilitada
            if not config_ambiente.enable_telemetria:
                if logger:
                    logger.info("Telemetria desabilitada por configuração")
                return None

            # Obtém configuração do cliente
            config_cliente = obter_config_cliente(config_ambiente)

            # Obtém campos fixos
            campos_fixos = obter_campos_fixos_para_tenant(
                tenant=tenant,
                empresa_detentora=empresa_detentora,
                cnpj_detentora=cnpj_detentora,
                empresa_sql=empresa_sql,
                cnpj_empresa=cnpj_empresa,
                servidor_sql=servidor_sql
            )

            # Cria e inicializa o serviço
            service = TelemetriaService.inicializar(
                config_cliente,
                campos_fixos,
                logger
            )

            if logger:
                logger.info("Sistema de telemetria inicializado com sucesso")

            return service

        except Exception as e:
            if logger:
                logger.error(f"Erro ao inicializar sistema de telemetria: {e}")
            return None

    @staticmethod
    def inicializar_sistema_simples(
        tenant: int,
        logger: Optional[logging.Logger] = None
    ) -> Optional[TelemetriaService]:
        """
        Inicializa o sistema de telemetria com configurações mínimas.

        Args:
            tenant: ID do tenant
            logger: Logger para registro de erros

        Returns:
            Instância do serviço de telemetria ou None se falhar
        """
        return TelemetriaFactory.inicializar_sistema(
            tenant=tenant,
            logger=logger
        )

    @staticmethod
    def obter_servico() -> Optional[TelemetriaService]:
        """
        Obtém a instância ativa do serviço de telemetria.

        Returns:
            Instância do serviço ou None se não inicializado
        """
        return TelemetriaService.get_instance()

    @staticmethod
    def verificar_status() -> Dict[str, Any]:
        """
        Verifica o status do sistema de telemetria.

        Returns:
            Dicionário com informações de status
        """
        service = TelemetriaService.get_instance()

        if not service:
            return {
                "status": "nao_inicializado",
                "mensagem": "Sistema de telemetria não foi inicializado"
            }

        try:
            # Testa se o cliente está funcionando
            config = service.client.config
            return {
                "status": "ativo",
                "api_url": config.api_url,
                "timeout": config.timeout,
                "max_retries": config.max_retries,
                "enable_telemetria": config.enable_telemetria
            }
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao verificar status: {e}"
            }

    @staticmethod
    def limpar_sistema():
        """Limpa e finaliza o sistema de telemetria."""
        service = TelemetriaService.get_instance()
        if service:
            try:
                service.close()
                TelemetriaService._instance = None
            except Exception:
                pass


def inicializar_telemetria(
    tenant: int,
    **kwargs
) -> Optional[TelemetriaService]:
    """
    Função de conveniência para inicializar telemetria.

    Args:
        tenant: ID do tenant
        **kwargs: Argumentos adicionais para configuração

    Returns:
        Instância do serviço de telemetria ou None se falhar
    """
    return TelemetriaFactory.inicializar_sistema(tenant, **kwargs)


def obter_telemetria() -> Optional[TelemetriaService]:
    """
    Função de conveniência para obter o serviço de telemetria.

    Returns:
        Instância do serviço ou None se não inicializado
    """
    return TelemetriaFactory.obter_servico()