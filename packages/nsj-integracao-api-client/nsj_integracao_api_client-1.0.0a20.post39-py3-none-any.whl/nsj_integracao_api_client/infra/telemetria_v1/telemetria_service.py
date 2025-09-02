"""
Serviço principal de telemetria.

Este módulo implementa o serviço central de telemetria que gerencia
todos os eventos e fornece métodos específicos para cada tipo de evento.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from .telemetria_client import TelemetriaClient, TelemetriaConfig
from .telemetria_metrics import obter_metricas


class TelemetriaService:
    """
    Serviço principal de telemetria.

    Responsável por gerenciar todos os eventos de telemetria e fornecer
    métodos específicos para cada tipo de evento implementado.
    """

    _instance: Optional['TelemetriaService'] = None

    def __init__(
        self,
        config: TelemetriaConfig,
        campos_fixos: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa o serviço de telemetria.

        Args:
            config: Configuração do cliente
            campos_fixos: Campos fixos para todos os eventos
            logger: Logger para registro de erros
        """
        self.client = TelemetriaClient(config, campos_fixos, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = obter_metricas()

        # Cache de eventos para correlação
        self._eventos_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> Optional['TelemetriaService']:
        """
        Obtém a instância global do serviço.

        Returns:
            Instância do serviço ou None se não inicializado
        """
        return cls._instance

    @classmethod
    def inicializar(
        cls,
        config: TelemetriaConfig,
        campos_fixos: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> 'TelemetriaService':
        """
        Inicializa a instância global do serviço.

        Args:
            config: Configuração do cliente
            campos_fixos: Campos fixos para todos os eventos
            logger: Logger para registro de erros

        Returns:
            Instância do serviço
        """
        cls._instance = cls(config, campos_fixos, logger)
        return cls._instance

    def enviar_evento(
        self,
        evento: str,
        resultado: str,
        dados_resultado: Dict[str, Any]
    ) -> bool:
        """
        Envia um evento de telemetria.

        Args:
            evento: Código do evento
            resultado: Descrição do resultado
            dados_resultado: Dados específicos do evento

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Adiciona ID de correlação se não existir
            if 'operacao_id' in dados_resultado:
                operacao_id = dados_resultado['operacao_id']
                if operacao_id not in self._eventos_cache:
                    self._eventos_cache[operacao_id] = {}

                # Adiciona informações de correlação
                dados_resultado['correlacao_id'] = operacao_id
                dados_resultado['sequencia_evento'] = len(self._eventos_cache[operacao_id]) + 1

            return self.client.enviar_evento(evento, resultado, dados_resultado)

        except Exception as e:
            self.logger.error(f"Erro ao enviar evento {evento}: {e}")
            return False

    # ============================================================================
    # EVENTOS DE CARGA INICIAL
    # ============================================================================

    def evento_inicio_carga(
        self,
        entidades_processar: int,
        tenant: int,
        ambiente: str,
        filtros_particionamento: Dict[str, str]
    ):
        """Evento ITG_INI_CARGA"""
        dados = {
            "entidades_processar": entidades_processar,
            "tenant": tenant,
            "ambiente": ambiente,
            "filtros_particionamento": filtros_particionamento,
            "timestamp_inicio": datetime.now().isoformat()
        }
        self.enviar_evento("ITG_INI_CARGA", "Iniciando carga inicial de dados", dados)

    def evento_fim_carga(
        self,
        entidades_processadas: int,
        total_registros: int,
        duracao_total_ms: float,
        memoria_maxima_mb: float
    ):
        """Evento ITG_FIM_CARGA"""
        dados = {
            "entidades_processadas": entidades_processadas,
            "total_registros": total_registros,
            "duracao_total_ms": duracao_total_ms,
            "registros_por_segundo": self.metrics.calcular_throughput(total_registros, duracao_total_ms),
            "memoria_maxima_mb": memoria_maxima_mb,
            "timestamp_fim": datetime.now().isoformat(),
            "status": "sucesso"
        }
        self.enviar_evento("ITG_FIM_CARGA", "Carga inicial finalizada com sucesso", dados)

    def evento_carga_entidade(
        self,
        entidade: str,
        ordem_processamento: int,
        total_entidades: int,
        filtros_aplicados: Dict[str, str]
    ):
        """Evento ITG_CARGA_ENTIDADE"""
        dados = {
            "entidade": entidade,
            "ordem_processamento": ordem_processamento,
            "total_entidades": total_entidades,
            "registros_processados": 0,
            "savepoint_atual": None,
            "timestamp_inicio": datetime.now().isoformat(),
            "filtros_aplicados": filtros_aplicados
        }
        self.enviar_evento("ITG_CARGA_ENTIDADE", "Processando entidade na carga inicial", dados)

    def evento_carga_lote(
        self,
        entidade: str,
        tamanho_lote: int,
        registros_processados: int,
        duracao_lote_ms: float,
        savepoint_proximo: str,
        memoria_utilizada_mb: float
    ):
        """Evento ITG_CARGA_LOTE"""
        dados = {
            "entidade": entidade,
            "tamanho_lote": tamanho_lote,
            "registros_processados": registros_processados,
            "duracao_lote_ms": duracao_lote_ms,
            "savepoint_proximo": savepoint_proximo,
            "memoria_utilizada_mb": memoria_utilizada_mb,
            "tipo_operacao": "carga_inicial",
            "registros_por_segundo": self.metrics.calcular_throughput(tamanho_lote, duracao_lote_ms)
        }
        self.enviar_evento("ITG_CARGA_LOTE", "Lote processado na carga inicial", dados)

    # ============================================================================
    # EVENTOS DE INTEGRAÇÃO CONTÍNUA
    # ============================================================================

    def evento_inicio_integracao(
        self,
        entidades_pendentes: int,
        tenant: int,
        ultima_integracao: str,
        filtros_ativos: List[str]
    ):
        """Evento ITG_INI_INTEG"""
        dados = {
            "entidades_pendentes": entidades_pendentes,
            "tenant": tenant,
            "ultima_integracao": ultima_integracao,
            "filtros_ativos": filtros_ativos,
            "timestamp_inicio": datetime.now().isoformat()
        }
        self.enviar_evento("ITG_INI_INTEG", "Iniciando integração contínua", dados)

    def evento_fim_integracao(
        self,
        entidades_processadas: int,
        total_envios: int,
        total_exclusoes: int,
        duracao_total_ms: float,
        memoria_maxima_mb: float
    ):
        """Evento ITG_FIM_INTEG"""
        dados = {
            "entidades_processadas": entidades_processadas,
            "total_envios": total_envios,
            "total_exclusoes": total_exclusoes,
            "duracao_total_ms": duracao_total_ms,
            "registros_por_segundo": self.metrics.calcular_throughput(total_envios + total_exclusoes, duracao_total_ms),
            "memoria_maxima_mb": memoria_maxima_mb,
            "timestamp_fim": datetime.now().isoformat(),
            "status": "sucesso"
        }
        self.enviar_evento("ITG_FIM_INTEG", "Integração finalizada com sucesso", dados)

    def evento_integracao_entidade(
        self,
        entidade: str,
        ordem_processamento: int,
        total_entidades: int,
        data_ultima_integracao: str,
        filtros_aplicados: Dict[str, str]
    ):
        """Evento ITG_INTEG_ENTIDADE"""
        dados = {
            "entidade": entidade,
            "ordem_processamento": ordem_processamento,
            "total_entidades": total_entidades,
            "data_ultima_integracao": data_ultima_integracao,
            "timestamp_inicio": datetime.now().isoformat(),
            "filtros_aplicados": filtros_aplicados
        }
        self.enviar_evento("ITG_INTEG_ENTIDADE", "Processando entidade na integração", dados)

    def evento_inicio_exclusoes(
        self,
        total_entidades_exclusao: int,
        ordem_processamento: str,
        estrategia: str,
        tamanho_lote_padrao: int
    ):
        """Evento ITG_INTEG_EXC_INI"""
        dados = {
            "total_entidades_exclusao": total_entidades_exclusao,
            "ordem_processamento": ordem_processamento,
            "estrategia": estrategia,
            "timestamp_inicio": datetime.now().isoformat(),
            "tamanho_lote_padrao": tamanho_lote_padrao
        }
        self.enviar_evento("ITG_INTEG_EXC_INI", "Iniciando processamento de exclusões", dados)

    def evento_fim_exclusoes(
        self,
        total_entidades_processadas: int,
        total_exclusoes: int,
        duracao_total_ms: float
    ):
        """Evento ITG_INTEG_EXC_FIM"""
        dados = {
            "total_entidades_processadas": total_entidades_processadas,
            "total_exclusoes": total_exclusoes,
            "duracao_total_ms": duracao_total_ms,
            "exclusoes_por_segundo": self.metrics.calcular_throughput(total_exclusoes, duracao_total_ms),
            "timestamp_fim": datetime.now().isoformat(),
            "status": "sucesso"
        }
        self.enviar_evento("ITG_INTEG_EXC_FIM", "Processamento de exclusões finalizado", dados)

    def evento_inicio_envios(
        self,
        total_entidades_envio: int,
        ordem_processamento: str,
        incluir_blobs: bool,
        verificar_diferencas: bool,
        tamanho_lote_padrao: int
    ):
        """Evento ITG_INTEG_ENV_INI"""
        dados = {
            "total_entidades_envio": total_entidades_envio,
            "ordem_processamento": ordem_processamento,
            "timestamp_inicio": datetime.now().isoformat(),
            "incluir_blobs": incluir_blobs,
            "verificar_diferencas": verificar_diferencas,
            "tamanho_lote_padrao": tamanho_lote_padrao
        }
        self.enviar_evento("ITG_INTEG_ENV_INI", "Iniciando processamento de envios", dados)

    def evento_fim_envios(
        self,
        total_entidades_processadas: int,
        total_envios: int,
        total_blobs_processados: int,
        duracao_total_ms: float
    ):
        """Evento ITG_INTEG_ENV_FIM"""
        dados = {
            "total_entidades_processadas": total_entidades_processadas,
            "total_envios": total_envios,
            "total_blobs_processados": total_blobs_processados,
            "duracao_total_ms": duracao_total_ms,
            "envios_por_segundo": self.metrics.calcular_throughput(total_envios, duracao_total_ms),
            "timestamp_fim": datetime.now().isoformat(),
            "status": "sucesso"
        }
        self.enviar_evento("ITG_INTEG_ENV_FIM", "Processamento de envios finalizado", dados)

    # ============================================================================
    # EVENTOS DE PROCESSAMENTO DE DADOS
    # ============================================================================

    def evento_envio_lote(
        self,
        entidade: str,
        tamanho_lote: int,
        registros_enviados: int,
        duracao_envio_ms: float,
        tamanho_dados_kb: float,
        tipo_operacao: str,
        filtros_aplicados: Dict[str, str],
        memoria_utilizada_mb: float
    ):
        """Evento ITG_ENV_LOTE"""
        dados = {
            "entidade": entidade,
            "tamanho_lote": tamanho_lote,
            "registros_enviados": registros_enviados,
            "duracao_envio_ms": duracao_envio_ms,
            "tamanho_dados_kb": tamanho_dados_kb,
            "tipo_operacao": tipo_operacao,
            "filtros_aplicados": filtros_aplicados,
            "memoria_utilizada_mb": memoria_utilizada_mb,
            "registros_por_segundo": self.metrics.calcular_throughput(registros_enviados, duracao_envio_ms)
        }
        self.enviar_evento("ITG_ENV_LOTE", "Lote de dados enviado com sucesso", dados)

    def evento_exclusao_lote(
        self,
        entidade: str,
        tamanho_lote: int,
        registros_excluidos: int,
        duracao_exclusao_ms: float,
        motivo_exclusao: str,
        data_ultima_integracao: str,
        memoria_utilizada_mb: float
    ):
        """Evento ITG_EXC_LOTE"""
        dados = {
            "entidade": entidade,
            "tamanho_lote": tamanho_lote,
            "registros_excluidos": registros_excluidos,
            "duracao_exclusao_ms": duracao_exclusao_ms,
            "motivo_exclusao": motivo_exclusao,
            "data_ultima_integracao": data_ultima_integracao,
            "memoria_utilizada_mb": memoria_utilizada_mb,
            "exclusoes_por_segundo": self.metrics.calcular_throughput(registros_excluidos, duracao_exclusao_ms)
        }
        self.enviar_evento("ITG_EXC_LOTE", "Lote de exclusões processado", dados)

    # ============================================================================
    # EVENTOS DE VERIFICAÇÃO DE INTEGRIDADE
    # ============================================================================

    def evento_inicio_verificacao(
        self,
        tipo_verificacao: str,
        entidades_verificar: int,
        correcao_automatica: bool,
        detalhar_diferencas: bool,
        parar_caso_diferencas: bool,
        tenant_verificacao: int
    ):
        """Evento ITG_INI_VERIF"""
        dados = {
            "tipo_verificacao": tipo_verificacao,
            "entidades_verificar": entidades_verificar,
            "correcao_automatica": correcao_automatica,
            "detalhar_diferencas": detalhar_diferencas,
            "parar_caso_diferencas": parar_caso_diferencas,
            "tenant_verificacao": tenant_verificacao,
            "timestamp_inicio": datetime.now().isoformat()
        }
        self.enviar_evento("ITG_INI_VERIF", "Iniciando verificação de integridade", dados)

    def evento_fim_verificacao(
        self,
        entidades_verificadas: int,
        total_diferencas: int,
        diferencas_criacao: int,
        diferencas_atualizacao: int,
        diferencas_exclusao: int,
        duracao_total_ms: float
    ):
        """Evento ITG_FIM_VERIF"""
        dados = {
            "entidades_verificadas": entidades_verificadas,
            "total_diferencas": total_diferencas,
            "diferencas_criacao": diferencas_criacao,
            "diferencas_atualizacao": diferencas_atualizacao,
            "diferencas_exclusao": diferencas_exclusao,
            "duracao_total_ms": duracao_total_ms,
            "timestamp_fim": datetime.now().isoformat(),
            "status": "com_diferencas" if total_diferencas > 0 else "sem_diferencas"
        }
        self.enviar_evento("ITG_FIM_VERIF", "Verificação de integridade finalizada", dados)

    def evento_verificacao_entidade(
        self,
        entidade: str,
        ordem_verificacao: int,
        total_entidades: int,
        registros_local: int,
        registros_remoto: int,
        duracao_verificacao_ms: float,
        tipo_verificacao: str
    ):
        """Evento ITG_VERIF_ENTIDADE"""
        dados = {
            "entidade": entidade,
            "ordem_verificacao": ordem_verificacao,
            "total_entidades": total_entidades,
            "registros_local": registros_local,
            "registros_remoto": registros_remoto,
            "duracao_verificacao_ms": duracao_verificacao_ms,
            "timestamp_inicio": datetime.now().isoformat(),
            "tipo_verificacao": tipo_verificacao
        }
        self.enviar_evento("ITG_VERIF_ENTIDADE", "Verificação de entidade específica", dados)

    def evento_verificacao_comparacao(
        self,
        entidade: str,
        registros_local: int,
        registros_remoto: int,
        registros_para_criar: int,
        registros_para_atualizar: int,
        registros_para_excluir: int,
        duracao_comparacao_ms: float,
        campos_verificados: List[str],
        memoria_utilizada_mb: float
    ):
        """Evento ITG_VERIF_COMPARACAO"""
        dados = {
            "entidade": entidade,
            "registros_local": registros_local,
            "registros_remoto": registros_remoto,
            "registros_para_criar": registros_para_criar,
            "registros_para_atualizar": registros_para_atualizar,
            "registros_para_excluir": registros_para_excluir,
            "duracao_comparacao_ms": duracao_comparacao_ms,
            "campos_verificados": campos_verificados,
            "memoria_utilizada_mb": memoria_utilizada_mb
        }
        self.enviar_evento("ITG_VERIF_COMPARACAO", "Comparação de dados concluída", dados)

    def evento_verificacao_diferenca(
        self,
        entidade: str,
        tipo_diferenca: str,
        quantidade_diferencas: int,
        campos_com_diferencas: List[str],
        exemplo_diferenca: Dict[str, Any]
    ):
        """Evento ITG_VERIF_DIFERENCA"""
        dados = {
            "entidade": entidade,
            "tipo_diferenca": tipo_diferenca,
            "quantidade_diferencas": quantidade_diferencas,
            "campos_com_diferencas": campos_com_diferencas,
            "exemplo_diferenca": exemplo_diferenca,
            "timestamp_deteccao": datetime.now().isoformat()
        }
        self.enviar_evento("ITG_VERIF_DIFERENCA", "Diferenças detectadas na verificação", dados)

    def evento_verificacao_correcao(
        self,
        entidade: str,
        quantidade_corrigida: int,
        tipo_correcao: str,
        duracao_correcao_ms: float,
        registros_por_segundo: float
    ):
        """Evento ITG_VERIF_CORRECAO"""
        dados = {
            "entidade": entidade,
            "quantidade_corrigida": quantidade_corrigida,
            "tipo_correcao": tipo_correcao,
            "duracao_correcao_ms": duracao_correcao_ms,
            "registros_por_segundo": registros_por_segundo,
            "timestamp_correcao": datetime.now().isoformat(),
            "status": "sucesso"
        }
        self.enviar_evento("ITG_VERIF_CORRECAO", "Correção automática de dados realizada", dados)

    def evento_verificacao_erro(
        self,
        entidade: str,
        tipo_erro: str,
        mensagem_erro: str,
        registros_processados: int,
        registros_pendentes: int,
        acao_recomendada: str
    ):
        """Evento ITG_VERIF_ERRO"""
        dados = {
            "entidade": entidade,
            "tipo_erro": tipo_erro,
            "mensagem_erro": mensagem_erro,
            "registros_processados": registros_processados,
            "registros_pendentes": registros_pendentes,
            "timestamp_erro": datetime.now().isoformat(),
            "acao_recomendada": acao_recomendada
        }
        self.enviar_evento("ITG_VERIF_ERRO", "Erro durante verificação", dados)

    def close(self):
        """Fecha o cliente de telemetria."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()