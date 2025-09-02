"""
Sistema de métricas de telemetria.

Este módulo implementa a captura automática de métricas de performance
como tempo de execução, uso de memória e outras métricas relevantes.
"""

import time
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class MetricasPerformance:
    """Métricas de performance coletadas."""
    duracao_ms: float = 0.0
    memoria_inicial_mb: float = 0.0
    memoria_atual_mb: float = 0.0
    memoria_maxima_mb: float = 0.0
    cpu_percentual: float = 0.0
    timestamp_inicio: datetime = field(default_factory=datetime.now)
    timestamp_fim: Optional[datetime] = None

    def finalizar(self):
        """Finaliza a coleta de métricas."""
        self.timestamp_fim = datetime.now()
        if self.timestamp_inicio:
            duracao = (self.timestamp_fim - self.timestamp_inicio).total_seconds()
            self.duracao_ms = duracao * 1000


class TelemetriaMetrics:
    """
    Sistema de métricas para telemetria.

    Responsável por capturar métricas de performance de forma automática
    e fornecer contexto para os eventos de telemetria.
    """

    def __init__(self):
        """Inicializa o sistema de métricas."""
        self._process = psutil.Process()
        self._lock = threading.Lock()
        self._metricas_ativas: Dict[str, MetricasPerformance] = {}

    @contextmanager
    def monitorar_operacao(self, operacao_id: str):
        """
        Context manager para monitorar uma operação.

        Args:
            operacao_id: Identificador único da operação

        Yields:
            Instância de MetricasPerformance
        """
        metricas = self._iniciar_monitoramento(operacao_id)
        try:
            yield metricas
        finally:
            self._finalizar_monitoramento(operacao_id)

    def _iniciar_monitoramento(self, operacao_id: str) -> MetricasPerformance:
        """
        Inicia o monitoramento de uma operação.

        Args:
            operacao_id: Identificador da operação

        Returns:
            Instância de métricas inicializada
        """
        with self._lock:
            metricas = MetricasPerformance()
            metricas.memoria_inicial_mb = self._obter_memoria_mb()
            self._metricas_ativas[operacao_id] = metricas
            return metricas

    def _finalizar_monitoramento(self, operacao_id: str):
        """
        Finaliza o monitoramento de uma operação.

        Args:
            operacao_id: Identificador da operação
        """
        with self._lock:
            if operacao_id in self._metricas_ativas:
                metricas = self._metricas_ativas[operacao_id]
                metricas.finalizar()
                metricas.memoria_atual_mb = self._obter_memoria_mb()
                metricas.memoria_maxima_mb = max(
                    metricas.memoria_inicial_mb,
                    metricas.memoria_atual_mb
                )
                metricas.cpu_percentual = self._obter_cpu_percentual()

    def obter_metricas(self, operacao_id: str) -> Optional[MetricasPerformance]:
        """
        Obtém as métricas de uma operação.

        Args:
            operacao_id: Identificador da operação

        Returns:
            Métricas da operação ou None se não encontrada
        """
        with self._lock:
            return self._metricas_ativas.get(operacao_id)

    def limpar_metricas(self, operacao_id: str):
        """
        Remove as métricas de uma operação.

        Args:
            operacao_id: Identificador da operação
        """
        with self._lock:
            self._metricas_ativas.pop(operacao_id, None)

    def _obter_memoria_mb(self) -> float:
        """
        Obtém o uso de memória em MB.

        Returns:
            Uso de memória em MB
        """
        try:
            memory_info = self._process.memory_info()
            return memory_info.rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _obter_cpu_percentual(self) -> float:
        """
        Obtém o percentual de CPU.

        Returns:
            Percentual de CPU
        """
        try:
            return self._process.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def obter_metricas_sistema(self) -> Dict[str, Any]:
        """
        Obtém métricas gerais do sistema.

        Returns:
            Dicionário com métricas do sistema
        """
        try:
            return {
                "memoria_total_mb": psutil.virtual_memory().total / (1024 * 1024),
                "memoria_disponivel_mb": psutil.virtual_memory().available / (1024 * 1024),
                "cpu_percentual_sistema": psutil.cpu_percent(interval=1),
                "disco_uso_percentual": psutil.disk_usage('/').percent
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}

    def calcular_throughput(self, registros_processados: int, duracao_ms: float) -> float:
        """
        Calcula o throughput (registros por segundo).

        Args:
            registros_processados: Quantidade de registros processados
            duracao_ms: Duração em milissegundos

        Returns:
            Throughput em registros por segundo
        """
        if duracao_ms <= 0:
            return 0.0
        return (registros_processados * 1000) / duracao_ms


# Instância global para uso em decorators
_metrics = TelemetriaMetrics()


def obter_metricas() -> TelemetriaMetrics:
    """
    Obtém a instância global de métricas.

    Returns:
        Instância de TelemetriaMetrics
    """
    return _metrics