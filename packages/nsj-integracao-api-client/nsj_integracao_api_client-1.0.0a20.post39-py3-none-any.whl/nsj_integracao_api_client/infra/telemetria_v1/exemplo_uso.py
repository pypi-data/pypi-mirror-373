"""
Exemplo de uso do sistema de telemetria.

Este arquivo demonstra como utilizar o sistema de telemetria
em diferentes cenários de integração.
"""

import logging
import time
from typing import List, Dict, Any
from .factory import TelemetriaFactory
from .telemetria_service import TelemetriaService


def exemplo_inicializacao():
    """Exemplo de inicialização do sistema de telemetria."""

    # Configuração do logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Inicialização simples
    service = TelemetriaFactory.inicializar_sistema_simples(
        tenant=12345,
        logger=logger
    )

    if service:
        logger.info("Telemetria inicializada com sucesso")
        return service
    else:
        logger.error("Falha ao inicializar telemetria")
        return None


def exemplo_carga_inicial(telemetria: TelemetriaService):
    """Exemplo de uso durante carga inicial."""

    # Simula dados de configuração
    entidades_processar = 15
    tenant = 12345
    ambiente = "PROD"
    filtros_particionamento = {
        "grupoempresarial": "1,2,3",
        "empresa": "10,20,30"
    }

    # Evento de início
    telemetria.evento_inicio_carga(
        entidades_processar=entidades_processar,
        tenant=tenant,
        ambiente=ambiente,
        filtros_particionamento=filtros_particionamento
    )

    # Simula processamento de entidades
    for i, entidade in enumerate(["ns.pessoas", "ns.empresas", "ns.estabelecimentos"]):
        # Evento de entidade
        telemetria.evento_carga_entidade(
            entidade=entidade,
            ordem_processamento=i + 1,
            total_entidades=entidades_processar,
            filtros_aplicados={"grupoempresarial": "1,2,3"}
        )

        # Simula processamento de lotes
        for j in range(3):
            time.sleep(0.1)  # Simula trabalho

            telemetria.evento_carga_lote(
                entidade=entidade,
                tamanho_lote=100,
                registros_processados=(j + 1) * 100,
                duracao_lote_ms=100,
                savepoint_proximo=f"ID_{(j + 1) * 100}",
                memoria_utilizada_mb=25.5
            )

    # Evento de fim
    telemetria.evento_fim_carga(
        entidades_processadas=entidades_processar,
        total_registros=4500,
        duracao_total_ms=3000,
        memoria_maxima_mb=156.7
    )


def exemplo_integracao_continua(telemetria: TelemetriaService):
    """Exemplo de uso durante integração contínua."""

    # Evento de início
    telemetria.evento_inicio_integracao(
        entidades_pendentes=8,
        tenant=12345,
        ultima_integracao="2024-01-15T08:00:00",
        filtros_ativos=["grupoempresarial", "empresa"]
    )

    # Evento de início de exclusões
    telemetria.evento_inicio_exclusoes(
        total_entidades_exclusao=8,
        ordem_processamento="reversa",
        estrategia="processamento_por_lote",
        tamanho_lote_padrao=100
    )

    # Simula processamento de exclusões
    time.sleep(0.5)

    # Evento de fim de exclusões
    telemetria.evento_fim_exclusoes(
        total_entidades_processadas=8,
        total_exclusoes=150,
        duracao_total_ms=500
    )

    # Evento de início de envios
    telemetria.evento_inicio_envios(
        total_entidades_envio=8,
        ordem_processamento="normal",
        incluir_blobs=True,
        verificar_diferencas=True,
        tamanho_lote_padrao=100
    )

    # Simula processamento de envios
    for i, entidade in enumerate(["ns.pessoas", "ns.empresas"]):
        telemetria.evento_integracao_entidade(
            entidade=entidade,
            ordem_processamento=i + 1,
            total_entidades=8,
            data_ultima_integracao="2024-01-15T08:00:00",
            filtros_aplicados={"lastupdate": "2024-01-15T08:00:00"}
        )

        # Simula envio de lotes
        for j in range(2):
            time.sleep(0.1)

            telemetria.evento_envio_lote(
                entidade=entidade,
                tamanho_lote=100,
                registros_enviados=100,
                duracao_envio_ms=150,
                tamanho_dados_kb=45.2,
                tipo_operacao="upsert",
                filtros_aplicados={"lastupdate": "2024-01-15T08:00:00"},
                memoria_utilizada_mb=32.1
            )

    # Evento de fim de envios
    telemetria.evento_fim_envios(
        total_entidades_processadas=8,
        total_envios=400,
        total_blobs_processados=25,
        duracao_total_ms=800
    )

    # Evento de fim da integração
    telemetria.evento_fim_integracao(
        entidades_processadas=8,
        total_envios=400,
        total_exclusoes=150,
        duracao_total_ms=1300,
        memoria_maxima_mb=89.3
    )


def exemplo_verificacao_integridade(telemetria: TelemetriaService):
    """Exemplo de uso durante verificação de integridade."""

    # Evento de início
    telemetria.evento_inicio_verificacao(
        tipo_verificacao="HASH",
        entidades_verificar=15,
        correcao_automatica=False,
        detalhar_diferencas=True,
        parar_caso_diferencas=False,
        tenant_verificacao=12345
    )

    # Simula verificação de entidades
    for i, entidade in enumerate(["ns.pessoas", "ns.empresas"]):
        telemetria.evento_verificacao_entidade(
            entidade=entidade,
            ordem_verificacao=i + 1,
            total_entidades=15,
            registros_local=1500,
            registros_remoto=1500,
            duracao_verificacao_ms=120000,
            tipo_verificacao="HASH"
        )

        # Simula comparação
        time.sleep(0.1)

        telemetria.evento_verificacao_comparacao(
            entidade=entidade,
            registros_local=1500,
            registros_remoto=1500,
            registros_para_criar=0,
            registros_para_atualizar=25,
            registros_para_excluir=5,
            duracao_comparacao_ms=3200,
            campos_verificados=["id", "nome", "email", "telefone"],
            memoria_utilizada_mb=67.8
        )

        # Simula detecção de diferenças
        if i == 0:  # Apenas para a primeira entidade
            telemetria.evento_verificacao_diferenca(
                entidade=entidade,
                tipo_diferenca="hash_incompativel",
                quantidade_diferencas=25,
                campos_com_diferencas=["nome", "email"],
                exemplo_diferenca={
                    "id": "12345",
                    "campo": "nome",
                    "valor_local": "João Silva",
                    "valor_remoto": "João da Silva"
                }
            )

    # Evento de fim
    telemetria.evento_fim_verificacao(
        entidades_verificadas=15,
        total_diferencas=30,
        diferencas_criacao=5,
        diferencas_atualizacao=20,
        diferencas_exclusao=5,
        duracao_total_ms=1800000
    )


def exemplo_uso_decorators():
    """Exemplo de uso dos decorators de telemetria."""

    from .telemetria_decorator import telemetria, telemetria_simples

    @telemetria("ITG_INI_CARGA", "ITG_FIM_CARGA")
    def executar_carga_inicial():
        """Função decorada com telemetria de entrada e saída."""
        print("Executando carga inicial...")
        time.sleep(0.5)  # Simula trabalho
        print("Carga inicial concluída")
        return "sucesso"

    @telemetria_simples("ITG_ENV_LOTE")
    def enviar_lote_dados():
        """Função decorada com telemetria simples."""
        print("Enviando lote de dados...")
        time.sleep(0.2)  # Simula trabalho
        print("Lote enviado")
        return "enviado"

    # Executa as funções decoradas
    resultado_carga = executar_carga_inicial()
    resultado_lote = enviar_lote_dados()

    print(f"Resultado carga: {resultado_carga}")
    print(f"Resultado lote: {resultado_lote}")


def exemplo_metricas():
    """Exemplo de uso do sistema de métricas."""

    from .telemetria_metrics import obter_metricas

    metrics = obter_metricas()

    # Monitora uma operação
    with metrics.monitorar_operacao("exemplo_operacao") as metricas:
        print("Executando operação...")
        time.sleep(0.3)  # Simula trabalho
        print("Operação concluída")

        # Métricas são coletadas automaticamente
        print(f"Duração: {metricas.duracao_ms:.2f}ms")
        print(f"Memória inicial: {metricas.memoria_inicial_mb:.2f}MB")
        print(f"Memória máxima: {metricas.memoria_maxima_mb:.2f}MB")
        print(f"CPU: {metricas.cpu_percentual:.2f}%")


def main():
    """Função principal de exemplo."""

    print("=== Exemplo de Uso do Sistema de Telemetria ===\n")

    # Inicializa telemetria
    telemetria = exemplo_inicializacao()
    if not telemetria:
        print("Não foi possível inicializar telemetria. Encerrando.")
        return

    try:
        # Exemplos de uso
        print("1. Exemplo de Carga Inicial")
        exemplo_carga_inicial(telemetria)
        print()

        print("2. Exemplo de Integração Contínua")
        exemplo_integracao_continua(telemetria)
        print()

        print("3. Exemplo de Verificação de Integridade")
        exemplo_verificacao_integridade(telemetria)
        print()

        print("4. Exemplo de Decorators")
        exemplo_uso_decorators()
        print()

        print("5. Exemplo de Métricas")
        exemplo_metricas()
        print()

        print("=== Todos os exemplos executados com sucesso! ===")

    except Exception as e:
        print(f"Erro durante execução dos exemplos: {e}")

    finally:
        # Limpa recursos
        telemetria.close()
        print("\nTelemetria finalizada.")


if __name__ == "__main__":
    main()