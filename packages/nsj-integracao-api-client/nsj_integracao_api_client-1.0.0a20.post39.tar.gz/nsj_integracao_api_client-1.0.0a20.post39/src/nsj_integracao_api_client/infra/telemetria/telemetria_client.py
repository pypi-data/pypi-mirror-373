"""
Cliente HTTP para comunicação com a API de telemetria.

Este módulo implementa o cliente responsável por enviar eventos de telemetria
para a API externa, incluindo retentativas e tratamento de erros.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


from nsj_gcf_utils.json_util import json_dumps

@dataclass
class TelemetriaConfig:
    """Configuração do cliente de telemetria."""

    url_api: str
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.3
    retry_status_forcelist: tuple = (500, 502, 503, 504)


class TelemetriaClient:
    """
    Cliente HTTP para envio de eventos de telemetria.

    Implementa retentativas automáticas, tratamento de erros e logging
    detalhado para garantir a entrega confiável dos eventos.
    """

    def __init__(self, config: TelemetriaConfig):
        """
        Inicializa o cliente de telemetria.

        Args:
            config: Configuração do cliente
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = self._criar_sessao()

    def _criar_sessao(self) -> requests.Session:
        """
        Cria uma sessão HTTP com configurações de retentativa.

        Returns:
            Sessão HTTP configurada
        """
        session = requests.Session()

        # Configurar retentativas
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=self.config.retry_status_forcelist,
            backoff_factor=self.config.retry_backoff_factor,
            allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configurar headers padrão
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "nsj_integracao_api_client/2.1.0"
        })

        return session

    def enviar_evento(self, payload: Dict[str, Any]) -> bool:
        """
        Envia um evento de telemetria para a API.

        Args:
            payload: Dados do evento a serem enviados

        Returns:
            True se o evento foi enviado com sucesso, False caso contrário
        """
        try:
            self.logger.debug("Enviando evento de telemetria: %s", payload.get("evento"))

            # planifica o resultado pois é o formato aceito
            if 'dadosresultado' in payload and type(payload['dadosresultado']) in [dict, list]:
                payload['dadosresultado'] = json_dumps(payload['dadosresultado'])

            response = self.session.post(
                url=self.config.url_api,
                json=payload,
                timeout=self.config.timeout
            )

            response.raise_for_status()

            self.logger.debug("Evento enviado com sucesso: %s", payload.get("evento"))
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error("Erro ao enviar evento de telemetria: %s", str(e))
            return False
        except Exception as e:
            self.logger.error("Erro inesperado ao enviar evento: %s", str(e))
            return False