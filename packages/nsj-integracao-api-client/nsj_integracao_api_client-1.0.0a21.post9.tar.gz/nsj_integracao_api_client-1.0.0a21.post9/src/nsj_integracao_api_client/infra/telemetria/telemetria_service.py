"""
Serviço principal de telemetria.

Este módulo implementa o serviço central de telemetria com suporte aos 8 eventos básicos:
- Carga Inicial (3 eventos): ITG_INI_CARGA, ITG_CARGA_ENTIDADE, ITG_FIM_CARGA
- Integração Contínua (3 eventos): ITG_INI_INTEG, ITG_INTEG_ENTIDADE, ITG_FIM_INTEG
- Verificação de Integridade (2 eventos): ITG_INI_VERIF, ITG_FIM_VERIF
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from nsj_integracao_api_client.infra.telemetria.telemetria_client import TelemetriaClient
from nsj_integracao_api_client.infra.telemetria.campos_fixos import obter_campos_fixos


class TelemetriaService:
    """
    Serviço central de telemetria que gerencia o envio de eventos.

    Implementa o padrão Singleton para garantir uma única instância
    do serviço em toda a aplicação.
    """

    _instancia: Optional['TelemetriaService'] = None
    _inicializado: bool = False


    def __new__(cls) -> 'TelemetriaService':
        """Implementa o padrão Singleton."""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia


    def __init__(self):
        """Inicializa o serviço de telemetria."""
        if not self._inicializado:
            self._client: Optional[TelemetriaClient] = None
            self._logger = logging.getLogger(__name__)
            self._inicializado = True
            self._empresadetentora = None
            self._cnpjdetentora = None


    def inicializar(
            self,
            empresadetentora: str,
            cnpjdetentora: str,
            client: TelemetriaClient,
        ) -> None:
        """
        Inicializa o serviço com o cliente de telemetria.

        Args:
            client: Cliente de telemetria configurado
        """
        self._client = client
        self._empresadetentora = empresadetentora
        self._cnpjdetentora = cnpjdetentora
        self._logger.info("TelemetriaService inicializado com sucesso")


    def _enviar_evento(self, evento: str, resultado: str, dados_resultado: Dict[str, Any]) -> None:
        """
        Envia um evento de telemetria.

        Args:
            evento: Código do evento
            resultado: Descrição do resultado
            dados_resultado: Dados contextuais do evento
        """
        if self._client is None:
            self._logger.warning("TelemetriaService não inicializado. Evento ignorado: %s", evento)
            return

        try:
            # Obter campos fixos
            campos_fixos = obter_campos_fixos(
                empresa_detentora=self._empresadetentora,
                cnpj_detentora=self._cnpjdetentora
            )

            # Construir payload completo
            payload = {
                **campos_fixos,
                "evento": evento,
                "resultado": resultado,
                "dadosresultado": dados_resultado
            }

            # Enviar evento
            self._client.enviar_evento(payload)

        except Exception as e:
            self._logger.error("Erro ao enviar evento de telemetria %s: %s", evento, str(e))

    # ============================================================================
    # EVENTOS DE CARGA INICIAL (3 eventos)
    # ============================================================================


    def evento_inicio_carga(
            self,
            correlation_id: str,
            entidades_processar: int, tenant: int,
            ambiente: str = "PROD",
        ) -> None:
        """
        Evento: ITG_INI_CARGA - Início da carga inicial

        Args:
            correlation_id: ID de correlação
            entidades_processar: Número de entidades a serem processadas
            tenant: ID do tenant
            ambiente: Ambiente de execução (PROD, QA, DEV)
            filtros_particionamento: Filtros de particionamento aplicados
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_processar": entidades_processar,
            "tenant": tenant,
            "ambiente": ambiente,
            "timestamp_inicio": datetime.now().isoformat()
        }

        self._enviar_evento(
            evento="ITG_INI_CARGA",
            resultado="Iniciando carga inicial de dados",
            dados_resultado=dados_resultado
        )


    def evento_carga_entidade(
            self,
            correlation_id: str,
            entidade: str,
            ordem_processamento: int,
            total_atualizacoes: int
        ) -> None:
        """
        Evento: ITG_CARGA_ENTIDADE - Processamento de entidade na carga

        Args:
            correlation_id: ID de correlação
            entidade: Nome da entidade sendo processada
            ordem_processamento: Ordem de processamento da entidade
            total_atualizacoes: Total de registros atualizados
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidade": entidade,
            "ordem_processamento": ordem_processamento,
            "total_atualizacoes": total_atualizacoes,
            "timestamp_inicio": datetime.now().isoformat()
        }

        self._enviar_evento(
            evento="ITG_CARGA_ENTIDADE",
            resultado="Processando entidade na carga inicial",
            dados_resultado=dados_resultado
        )


    def evento_fim_carga(
            self,
            correlation_id: str,
            entidades_processadas: int,
            total_registros: int,
            duracao_total_ms: int,
            status: str
        ) -> None:
        """
        Evento: ITG_FIM_CARGA - Fim da carga inicial

        Args:
            correlation_id: ID de correlação
            entidades_processadas: Número de entidades processadas
            total_registros: Total de registros processados
            duracao_total_ms: Duração total em milissegundos
            status: Status da integração
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_processadas": entidades_processadas,
            "total_registros": total_registros,
            "duracao_total_ms": duracao_total_ms,
            "registros_por_segundo": round(total_registros / (duracao_total_ms / 1000), 1) if duracao_total_ms > 0 else 0,
            "timestamp_fim": datetime.now().isoformat(),
            "status": status
        }

        self._enviar_evento(
            evento="ITG_FIM_CARGA",
            resultado="Carga inicial finalizada com sucesso",
            dados_resultado=dados_resultado
        )

    # ============================================================================
    # EVENTOS DE INTEGRAÇÃO CONTÍNUA (3 eventos)
    # ============================================================================


    def evento_inicio_integracao(
            self,
            correlation_id: str,
            entidades_pendentes: int,
            tenant: int,
            ambiente: str = "PROD"
        ) -> None:
        """
        Evento: ITG_INI_INTEG - Início da integração

        Args:
            correlation_id: ID de correlação
            entidades_pendentes: Número de entidades pendentes
            tenant: ID do tenant
            ambiente: Ambiente de execução (PROD, QA, DEV)
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_pendentes": entidades_pendentes,
            "tenant": tenant,
            "ambiente": ambiente,
            "timestamp_inicio": datetime.now().isoformat()
        }

        self._enviar_evento(
            evento="ITG_INI_INTEG",
            resultado="Iniciando integração contínua",
            dados_resultado=dados_resultado
        )


    def evento_integracao_entidade(
            self,
            correlation_id: str,
            entidade: str,
            ordem_processamento: int,
            total_exclusoes: int,
            total_atualizacoes: int,
            data_ultima_integracao: Optional[str] = None
        ) -> None:
        """
        Evento: ITG_INTEG_ENTIDADE - Processamento de entidade na integração

        Args:
            correlation_id: ID de correlação
            entidade: Nome da entidade sendo processada
            ordem_processamento: Ordem de processamento da entidade
            total_exclusoes: Total de registros excluídos
            total_atualizacoes: Total de registros atualizados
            data_ultima_integracao: Data da última integração
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidade": entidade,
            "ordem_processamento": ordem_processamento,
            "total_exclusoes": total_exclusoes,
            "total_atualizacoes": total_atualizacoes,
            "data_ultima_integracao": data_ultima_integracao,
            "timestamp_inicio": datetime.now().isoformat()
        }

        self._enviar_evento(
            evento="ITG_INTEG_ENTIDADE",
            resultado="Processando entidade na integração",
            dados_resultado=dados_resultado
        )


    def evento_fim_integracao(
            self,
            correlation_id: str,
            entidades_processadas: int,
            total_exclusoes: int,
            total_atualizacoes: int,
            duracao_total_ms: int,
            status: str
        ) -> None:
        """
        Evento: ITG_FIM_INTEG - Fim da integração

        Args:
            correlation_id: ID de correlação
            entidades_processadas: Número de entidades processadas
            total_exclusoes: Total de registros excluídos
            total_atualizacoes: Total de registros enviados
            duracao_total_ms: Duração total em milissegundos
            status: Status da integração
        """
        total_registros = total_atualizacoes + total_exclusoes

        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_processadas": entidades_processadas,
            "total_atualizacoes": total_atualizacoes,
            "total_exclusoes": total_exclusoes,
            "duracao_total_ms": duracao_total_ms,
            "registros_por_segundo": round(total_registros / (duracao_total_ms / 1000), 1) if duracao_total_ms > 0 else 0,
            "timestamp_fim": datetime.now().isoformat(),
            "status": status
        }

        self._enviar_evento(
            evento="ITG_FIM_INTEG",
            resultado="Integração finalizada com sucesso",
            dados_resultado=dados_resultado
        )

    # ============================================================================
    # EVENTOS DE VERIFICAÇÃO DE INTEGRIDADE (2 eventos)
    # ============================================================================


    def evento_inicio_verificacao(
            self,
            correlation_id: str,
            entidades_verificar: int,
            tenant: int,
            ambiente: str = "PROD",
            tipo_verificacao: str = "HASH"
        ) -> None:
        """
        Evento: ITG_INI_VERIF - Início da verificação de integridade

        Args:
            correlation_id: ID de correlação
            entidades_verificar: Número de entidades a serem verificadas
            tenant: ID do tenant
            ambiente: Ambiente de execução (PROD, QA, DEV)
            tipo_verificacao: Tipo de verificação (HASH, COMPARACAO, etc.)
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_verificar": entidades_verificar,
            "tenant": tenant,
            "ambiente": ambiente,
            "tipo_verificacao": tipo_verificacao,
            "campos_verificados": ["id", "nome", "email", "telefone"],  # Campos padrão
            "timestamp_inicio": datetime.now().isoformat()
        }

        self._enviar_evento(
            evento="ITG_INI_VERIF",
            resultado="Iniciando verificação de integridade",
            dados_resultado=dados_resultado
        )


    def evento_fim_verificacao(
            self,
            correlation_id: int,
            entidades_verificadas: int,
            total_diferencas: int,
            duracao_total_ms: int
        ) -> None:
        """
        Evento: ITG_FIM_VERIF - Fim da verificação de integridade

        Args:
            correlation_id: ID de correlação
            entidades_verificadas: Número de entidades verificadas
            total_diferencas: Total de diferenças encontradas
            duracao_total_ms: Duração total em milissegundos
        """
        dados_resultado = {
            "correlation_id": correlation_id,
            "entidades_verificadas": entidades_verificadas,
            "total_diferencas": total_diferencas,
            "diferencas_criacao": 0,  # Será calculado se necessário
            "diferencas_atualizacao": 0,  # Será calculado se necessário
            "diferencas_exclusao": 0,  # Será calculado se necessário
            "duracao_total_ms": duracao_total_ms,
            "timestamp_fim": datetime.now().isoformat(),
            "status": "com_diferencas" if total_diferencas > 0 else "sem_diferencas"
        }

        self._enviar_evento(
            evento="ITG_FIM_VERIF",
            resultado="Verificação de integridade finalizada",
            dados_resultado=dados_resultado
        )