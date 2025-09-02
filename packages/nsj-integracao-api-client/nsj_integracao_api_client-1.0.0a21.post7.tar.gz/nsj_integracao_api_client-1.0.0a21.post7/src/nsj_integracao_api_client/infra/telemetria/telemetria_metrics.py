"""
Métricas de performance para telemetria.

Este módulo implementa a captura automática de métricas de performance
como tempo de execução, uso de memória e CPU durante operações.
"""

import time
import psutil
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from contextlib import contextmanager


@dataclass
class MetricasPerformance:
    """Dados de métricas de performance."""

    operacao: str
    duracao_ms: float
    memoria_inicial_mb: float
    memoria_final_mb: float
    memoria_maxima_mb: float
    cpu_percentual: float
    timestamp_inicio: float
    timestamp_fim: float
    status: str = "sucesso"
    erro: Optional[str] = None
    dados_extras: Dict[str, Any] = field(default_factory=dict)


class TelemetriaMetrics:
    """
    Sistema de métricas de performance para telemetria.

    Captura automaticamente métricas de tempo, memória e CPU
    durante a execução de operações.
    """

    def __init__(self):
        """Inicializa o sistema de métricas."""
        self.logger = logging.getLogger(__name__)
        self._metricas: List[MetricasPerformance] = []
        self._processo = psutil.Process()

    def _obter_uso_memoria_mb(self) -> float:
        """
        Obtém o uso de memória em MB.

        Returns:
            Uso de memória em MB
        """
        try:
            return self._processo.memory_info().rss / 1024 / 1024
        except Exception as e:
            self.logger.warning("Erro ao obter uso de memória: %s", str(e))
            return 0.0

    def _obter_uso_cpu_percentual(self) -> float:
        """
        Obtém o uso de CPU em percentual.

        Returns:
            Uso de CPU em percentual
        """
        try:
            return self._processo.cpu_percent(interval=0.1)
        except Exception as e:
            self.logger.warning("Erro ao obter uso de CPU: %s", str(e))
            return 0.0

    @contextmanager
    def monitorar_operacao(self, nome_operacao: str,
                          dados_extras: Optional[Dict[str, Any]] = None):
        """
        Context manager para monitorar uma operação.

        Args:
            nome_operacao: Nome da operação a ser monitorada
            dados_extras: Dados extras a serem incluídos nas métricas

        Yields:
            Objeto com métricas da operação
        """
        timestamp_inicio = time.time()
        memoria_inicial = self._obter_uso_memoria_mb()
        cpu_inicial = self._obter_uso_cpu_percentual()

        metricas = MetricasPerformance(
            operacao=nome_operacao,
            duracao_ms=0.0,
            memoria_inicial_mb=memoria_inicial,
            memoria_final_mb=memoria_inicial,
            memoria_maxima_mb=memoria_inicial,
            cpu_percentual=cpu_inicial,
            timestamp_inicio=timestamp_inicio,
            timestamp_fim=timestamp_inicio,
            dados_extras=dados_extras or {}
        )

        try:
            yield metricas

            # Operação concluída com sucesso
            metricas.status = "sucesso"

        except Exception as e:
            # Operação falhou
            metricas.status = "erro"
            metricas.erro = str(e)
            self.logger.error("Erro na operação %s: %s", nome_operacao, str(e))
            raise

        finally:
            # Finalizar métricas
            timestamp_fim = time.time()
            memoria_final = self._obter_uso_memoria_mb()

            metricas.timestamp_fim = timestamp_fim
            metricas.duracao_ms = (timestamp_fim - timestamp_inicio) * 1000
            metricas.memoria_final_mb = memoria_final
            metricas.memoria_maxima_mb = max(memoria_inicial, memoria_final)

            # Adicionar às métricas coletadas
            self._metricas.append(metricas)

            self.logger.debug(
                "Operação %s concluída: %.2fms, memória: %.2fMB",
                nome_operacao, metricas.duracao_ms, metricas.memoria_maxima_mb
            )

    def obter_metricas(self) -> List[MetricasPerformance]:
        """
        Obtém todas as métricas coletadas.

        Returns:
            Lista de métricas coletadas
        """
        return self._metricas.copy()


# Instância global para uso em decoradores
_instancia_metricas = TelemetriaMetrics()


def obter_metricas() -> List[MetricasPerformance]:
    """
    Obtém todas as métricas coletadas.

    Returns:
        Lista de métricas coletadas
    """
    return _instancia_metricas.obter_metricas()