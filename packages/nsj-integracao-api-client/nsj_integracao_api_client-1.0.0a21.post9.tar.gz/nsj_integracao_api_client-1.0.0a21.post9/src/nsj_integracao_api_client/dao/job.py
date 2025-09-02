from typing import List
from datetime import datetime
from nsj_gcf_utils.db_adapter2 import DBAdapter2
import uuid

class JobDAO:

    _db: DBAdapter2

    def __init__(self, db: DBAdapter2):
        self._db = db

    def get_job_type_by_code(self, codigo):
        """
        Retorna o JobType correspondente ao CODIGO passado.
        """

        sql = """
            select
                codigo as codigo,
                funcao as funcao,
                modoexecucao as modo_execucao,
                schema as schema,
                sistema as sistema,
                urlscript as url_script,
                pacote as pacote,
                classe as classe,
                versao as versao
            from
                util.jobtypes
            where
                codigo = :codigo
        """

        return self._db.execute_query_first_result(sql, codigo=codigo)


    def cria_job_type(self, sistema, modoexecucao, codigo):

        sql = """
            insert into util.jobtypes (
            codigo,
            sistema,
            modoexecucao
            ) values (
            :codigo,
            :sistema,
            :modoexecucao
            ) returning
                codigo as codigo,
                funcao as funcao,
                modoexecucao as modo_execucao,
                schema as schema,
                sistema as sistema,
                urlscript as url_script,
                pacote as pacote,
                classe as classe,
                versao as versao
        """

        rowcount, _ = self._db.execute(sql, codigo=codigo, sistema=sistema, modoexecucao=modoexecucao)

        if rowcount!=1:
            raise Exception(
                "Erro ao registrar grupos empresariais no banco de dados"
            )


    def get_agendamento_integracao(self):

        sql = """
            select
                a.jobschedule as id,
                b.codigo,
                a.descricao,
                a.jobtype,
                a.entrada,
                a.tipoagendamento,
                a.intervaloagendamento as intervalo,
                a.status
            from util.jobschedule a
            join util.jobtypes b on ( b.jobtype = a.jobtype )
            where
                b.codigo = 'INTEGRACAO_APIS' and
                a.tenant = 0 and
                a.tipoagendamento = 1
        """

        return self._db.execute_query_first_result(sql)


    def agenda_job(self, entrada, intervalo):

        # tipoagendamento -
        # 0 - Agendado para todos os dias, no horário do campo "agendamento" (ignorando o dia do mesmo campo);
        # 1 - Agendado para executar a cada X minutos (de acordo com o campo intervaloagendamento);
        # 2 - Agendado para o momento definido no campo agendamento;

        sql = """
            INSERT INTO util.jobschedule (
                codigo,
                descricao,
                jobtype,
                entrada,
                tipoagendamento,
                intervaloagendamento
            ) VALUES (
                'INTEGRACAO_NASAJON',
                'Piloto do Job de integração por apis para substituir o symmetric',
                (SELECT jobtype FROM util.jobtypes WHERE codigo='INTEGRACAO_APIS'),
                :entrada,
                1,
                :intevalo --intervalo de execucao (minutos)
            );
        """
        rowcount, _ = self._db.execute(sql, entrada=entrada, intevalo=intervalo)

        if rowcount!=1:
            raise Exception(
                "Erro ao registrar agendamento no banco de dados"
            )


    def atualiza_job(self, agendamento, entrada, intervalo):

        # tipoagendamento -
        # 0 - Agendado para todos os dias, no horário do campo "agendamento" (ignorando o dia do mesmo campo);
        # 1 - Agendado para executar a cada X minutos (de acordo com o campo intervaloagendamento);
        # 2 - Agendado para o momento definido no campo agendamento;

        sql = """
            UPDATE util.jobschedule
            SET
                status = 0,
                intervaloagendamento = :intevalo,
                entrada = :entrada
            WHERE
                jobschedule = :agendamento;
        """
        rowcount, _ = self._db.execute(sql, agendamento=agendamento, entrada=entrada, intevalo=intervalo)

        if rowcount!=1:
            raise Exception(
                "Erro ao registrar agendamento no banco de dados"
            )


    def cancela_agendamento(self, agendamento):
        sql = """
            UPDATE util.jobschedule
            SET STATUS = 3
            WHERE jobschedule = :jobschedule
        """
        rowcount, _ = self._db.execute(sql, jobschedule=agendamento)

        if rowcount!=1:
            raise Exception(
                "Erro ao excluir agendamento no banco de dados"
            )