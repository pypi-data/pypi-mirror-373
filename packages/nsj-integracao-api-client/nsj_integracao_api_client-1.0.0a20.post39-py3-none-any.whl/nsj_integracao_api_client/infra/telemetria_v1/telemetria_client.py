"""
Cliente de telemetria para comunicação com a API externa.

Este módulo implementa o cliente responsável por enviar eventos de telemetria
para a API de telemetria, incluindo retentativas e tratamento de erros.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from dataclasses import dataclass, asdict


@dataclass
class TelemetriaConfig:
    """Configuração para o cliente de telemetria."""
    api_url: str = "http://telemetria.nasajon.com.br/api/events"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5
    enable_telemetria: bool = True


class TelemetriaClient:
    """
    Cliente para envio de eventos de telemetria.

    Responsável por enviar eventos para a API de telemetria com suporte
    a retentativas e tratamento de erros.
    """

    def __init__(
        self,
        config: TelemetriaConfig,
        campos_fixos: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa o cliente de telemetria.

        Args:
            config: Configuração do cliente
            campos_fixos: Campos fixos que serão incluídos em todos os eventos
            logger: Logger para registro de erros
        """
        self.config = config
        self.campos_fixos = campos_fixos
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()

    def enviar_evento(
        self,
        evento: str,
        resultado: str,
        dados_resultado: Dict[str, Any]
    ) -> bool:
        """
        Envia um evento de telemetria para a API.

        Args:
            evento: Código do evento
            resultado: Descrição do resultado
            dados_resultado: Dados específicos do evento

        Returns:
            True se o evento foi enviado com sucesso, False caso contrário
        """
        if not self.config.enable_telemetria:
            return True

        try:
            payload = self._construir_payload(evento, resultado, dados_resultado)
            return self._enviar_com_retry(payload)
        except Exception as e:
            self.logger.error(f"Erro ao enviar evento de telemetria: {e}")
            return False

    def _construir_payload(
        self,
        evento: str,
        resultado: str,
        dados_resultado: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói o payload completo do evento.

        Args:
            evento: Código do evento
            resultado: Descrição do resultado
            dados_resultado: Dados específicos do evento

        Returns:
            Payload completo do evento
        """
        # Adiciona timestamp do evento se não existir
        if 'timestamp_evento' not in dados_resultado:
            dados_resultado['timestamp_evento'] = datetime.now().isoformat()

        payload = {
            **self.campos_fixos,
            "evento": evento,
            "resultado": resultado,
            "dadosresultado": dados_resultado
        }

        return payload

    def _enviar_com_retry(self, payload: Dict[str, Any]) -> bool:
        """
        Envia o payload com suporte a retentativas.

        Args:
            payload: Payload do evento

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        for tentativa in range(self.config.max_retries):
            try:
                response = self.session.post(
                    self.config.api_url,
                    json=payload,
                    timeout=self.config.timeout,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    return True
                else:
                    self.logger.warning(
                        f"API retornou status {response.status_code} na tentativa {tentativa + 1}"
                    )

            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Erro de requisição na tentativa {tentativa + 1}: {e}"
                )

            # Aguarda antes da próxima tentativa (exceto na última)
            if tentativa < self.config.max_retries - 1:
                import time
                time.sleep(self.config.retry_delay)

        self.logger.error(
            f"Falha ao enviar evento após {self.config.max_retries} tentativas"
        )
        return False

    def close(self):
        """Fecha a sessão HTTP."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()