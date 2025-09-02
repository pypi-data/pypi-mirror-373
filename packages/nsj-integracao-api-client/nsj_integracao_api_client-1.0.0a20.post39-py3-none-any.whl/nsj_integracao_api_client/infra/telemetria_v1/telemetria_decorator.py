"""
Decorator de telemetria para métodos.

Este módulo implementa decorators que automatizam a captura de eventos
de telemetria para entrada e saída de métodos.
"""

import functools
import uuid
from typing import Callable, Any, Dict, Optional
from .telemetria_metrics import obter_metricas


def telemetria(
    evento_entrada: str,
    evento_saida: str,
    extrair_contexto: Optional[Callable] = None
):
    """
    Decorator para capturar eventos de telemetria de entrada e saída.

    Args:
        evento_entrada: Código do evento de entrada
        evento_saida: Código do evento de saída
        extrair_contexto: Função para extrair contexto adicional dos argumentos

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gera ID único para a operação
            operacao_id = str(uuid.uuid4())

            # Obtém instância de métricas
            metrics = obter_metricas()

            # Extrai contexto se fornecido
            contexto = {}
            if extrair_contexto:
                try:
                    contexto = extrair_contexto(*args, **kwargs) or {}
                except Exception:
                    contexto = {}

            # Adiciona informações básicas do contexto
            contexto.update({
                "funcao": func.__name__,
                "modulo": func.__module__,
                "operacao_id": operacao_id
            })

            # Envia evento de entrada
            from .telemetria_service import TelemetriaService
            telemetria_service = TelemetriaService.get_instance()

            if telemetria_service:
                telemetria_service.enviar_evento(
                    evento_entrada,
                    f"Iniciando execução de {func.__name__}",
                    contexto
                )

            # Monitora a operação
            with metrics.monitorar_operacao(operacao_id) as metricas:
                try:
                    # Executa a função
                    resultado = func(*args, **kwargs)

                    # Prepara contexto de saída
                    contexto_saida = contexto.copy()
                    contexto_saida.update({
                        "status": "sucesso",
                        "duracao_ms": metricas.duracao_ms,
                        "memoria_utilizada_mb": metricas.memoria_maxima_mb
                    })

                    # Envia evento de saída
                    if telemetria_service:
                        telemetria_service.enviar_evento(
                            evento_saida,
                            f"Execução de {func.__name__} concluída com sucesso",
                            contexto_saida
                        )

                    return resultado

                except Exception as e:
                    # Prepara contexto de erro
                    contexto_erro = contexto.copy()
                    contexto_erro.update({
                        "status": "erro",
                        "tipo_erro": type(e).__name__,
                        "mensagem_erro": str(e),
                        "duracao_ms": metricas.duracao_ms,
                        "memoria_utilizada_mb": metricas.memoria_maxima_mb
                    })

                    # Envia evento de erro
                    if telemetria_service:
                        telemetria_service.enviar_evento(
                            evento_saida,
                            f"Execução de {func.__name__} falhou",
                            contexto_erro
                        )

                    # Re-lança a exceção
                    raise
                finally:
                    # Limpa as métricas
                    metrics.limpar_metricas(operacao_id)

        return wrapper
    return decorator


def telemetria_simples(evento: str):
    """
    Decorator simples para capturar apenas um evento.

    Args:
        evento: Código do evento

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gera ID único para a operação
            operacao_id = str(uuid.uuid4())

            # Obtém instância de métricas
            metrics = obter_metricas()

            # Prepara contexto
            contexto = {
                "funcao": func.__name__,
                "modulo": func.__module__,
                "operacao_id": operacao_id
            }

            # Envia evento de início
            from .telemetria_service import TelemetriaService
            telemetria_service = TelemetriaService.get_instance()

            if telemetria_service:
                telemetria_service.enviar_evento(
                    evento,
                    f"Executando {func.__name__}",
                    contexto
                )

            # Monitora a operação
            with metrics.monitorar_operacao(operacao_id) as metricas:
                try:
                    resultado = func(*args, **kwargs)

                    # Atualiza contexto com métricas
                    contexto.update({
                        "status": "sucesso",
                        "duracao_ms": metricas.duracao_ms,
                        "memoria_utilizada_mb": metricas.memoria_maxima_mb
                    })

                    return resultado

                except Exception as e:
                    # Atualiza contexto com informações de erro
                    contexto.update({
                        "status": "erro",
                        "tipo_erro": type(e).__name__,
                        "mensagem_erro": str(e),
                        "duracao_ms": metricas.duracao_ms,
                        "memoria_utilizada_mb": metricas.memoria_maxima_mb
                    })

                    raise
                finally:
                    # Limpa as métricas
                    metrics.limpar_metricas(operacao_id)

        return wrapper
    return decorator