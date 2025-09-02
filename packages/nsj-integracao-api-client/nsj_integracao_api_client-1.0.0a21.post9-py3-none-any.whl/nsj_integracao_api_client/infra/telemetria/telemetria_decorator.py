"""
Decoradores para captura automática de eventos de telemetria.

Este módulo implementa decoradores que permitem capturar automaticamente
eventos de telemetria no início e fim de funções, ou eventos simples.
"""

import functools
import logging
import time
from typing import Callable, Optional
from nsj_integracao_api_client.infra.telemetria.telemetria_service import TelemetriaService
from nsj_integracao_api_client.infra.telemetria.telemetria_metrics import TelemetriaMetrics


def telemetria(evento_inicio: str, evento_fim: Optional[str] = None):
    """
    Decorador para capturar eventos de telemetria no início e fim de uma função.

    Args:
        evento_inicio: Código do evento de início
        evento_fim: Código do evento de fim (opcional, usa evento_inicio + "_FIM" se não fornecido)

    Returns:
        Decorador da função
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obter instâncias
            telemetria_service = TelemetriaService()
            metrics = TelemetriaMetrics()

            # Determinar evento de fim
            evento_fim_final = evento_fim or f"{evento_inicio}_FIM"

            # Dados do evento de início
            dados_inicio = {
                "funcao": func.__name__,
                "modulo": func.__module__,
                "timestamp_inicio": time.time()
            }

            # Enviar evento de início
            try:
                telemetria_service._enviar_evento(
                    evento=evento_inicio,
                    resultado=f"Iniciando execução da função {func.__name__}",
                    dados_resultado=dados_inicio
                )
            except Exception as e:
                logging.getLogger(__name__).warning(
                    "Erro ao enviar evento de início %s: %s", evento_inicio, str(e)
                )

            # Executar função com monitoramento de métricas
            try:
                with metrics.monitorar_operacao(func.__name__) as metricas:
                    resultado = func(*args, **kwargs)
                    metricas.dados_extras["resultado_sucesso"] = True
                    return resultado

            except Exception as e:
                # Capturar erro nas métricas
                with metrics.monitorar_operacao(func.__name__) as metricas:
                    metricas.status = "erro"
                    metricas.erro = str(e)
                    metricas.dados_extras["resultado_sucesso"] = False
                    raise

            finally:
                # Dados do evento de fim
                dados_fim = {
                    "funcao": func.__name__,
                    "modulo": func.__module__,
                    "timestamp_fim": time.time(),
                    "duracao_ms": metricas.duracao_ms if 'metricas' in locals() else 0,
                    "memoria_utilizada_mb": metricas.memoria_maxima_mb if 'metricas' in locals() else 0,
                    "status": metricas.status if 'metricas' in locals() else "desconhecido"
                }

                # Enviar evento de fim
                try:
                    telemetria_service._enviar_evento(
                        evento=evento_fim_final,
                        resultado=f"Finalizando execução da função {func.__name__}",
                        dados_resultado=dados_fim
                    )
                except Exception as e:
                    logging.getLogger(__name__).warning(
                        "Erro ao enviar evento de fim %s: %s", evento_fim_final, str(e)
                    )

        return wrapper
    return decorator


def telemetria_simples(evento: str):
    """
    Decorador para capturar um evento simples de telemetria.

    Args:
        evento: Código do evento a ser enviado

    Returns:
        Decorador da função
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obter instância do serviço
            telemetria_service = TelemetriaService()

            # Dados do evento
            dados_evento = {
                "funcao": func.__name__,
                "modulo": func.__module__,
                "timestamp": time.time(),
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            }

            # Executar função
            try:
                resultado = func(*args, **kwargs)

                # Adicionar informações de sucesso
                dados_evento["status"] = "sucesso"
                dados_evento["resultado_tipo"] = type(resultado).__name__

                # Enviar evento
                try:
                    telemetria_service._enviar_evento(
                        evento=evento,
                        resultado=f"Execução bem-sucedida da função {func.__name__}",
                        dados_resultado=dados_evento
                    )
                except Exception as e:
                    logging.getLogger(__name__).warning(
                        "Erro ao enviar evento %s: %s", evento, str(e)
                    )

                return resultado

            except Exception as e:
                # Adicionar informações de erro
                dados_evento["status"] = "erro"
                dados_evento["erro"] = str(e)
                dados_evento["tipo_erro"] = type(e).__name__

                # Enviar evento de erro
                try:
                    telemetria_service._enviar_evento(
                        evento=evento,
                        resultado=f"Erro na execução da função {func.__name__}",
                        dados_resultado=dados_evento
                    )
                except Exception as telemetria_error:
                    logging.getLogger(__name__).warning(
                        "Erro ao enviar evento %s: %s", evento, str(telemetria_error)
                    )

                # Re-levantar o erro original
                raise

        return wrapper
    return decorator