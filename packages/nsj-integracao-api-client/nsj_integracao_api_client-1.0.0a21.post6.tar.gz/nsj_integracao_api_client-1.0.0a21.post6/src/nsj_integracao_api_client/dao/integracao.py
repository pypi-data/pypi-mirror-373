import hashlib
from typing import List
from datetime import datetime
from nsj_gcf_utils.db_adapter2 import DBAdapter2
from nsj_gcf_utils.json_util import json_dumps

class IntegracaoDAO:
    """
    Classe responsável pelas operacoees de CRUD ao banco de dados
    """
    _db: DBAdapter2


    def __init__(self, db: DBAdapter2 = None):
        self._db = db


    def begin(self):
        """
        Inicia uma transação no banco de dados
        """
        self._db.begin()


    def commit(self):
        """
        Faz commit na transação corrente no banco de dados (se houver uma).

        Não dá erro, se não houver uma transação.
        """
        self._db.commit()


    def rollback(self):
        """
        Faz rollback da transação corrente no banco de dados (se houver uma).

        Não dá erro, se não houver uma transação.
        """
        self._db.rollback()


    def filtros_integracao_entidade(self, entidade: str):
        sql = """SELECT
                filtros_integracao
            FROM util.entidades_integracao
            WHERE entidade = :entidade"""
        data = self._db.execute_query_first_result(sql, entidade=entidade)

        return data['filtros_integracao'] if data else []


    def data_ultima_integracao(self, entidade: str):
        sql = """SELECT
                data_ultima_integracao
            FROM util.entidades_integracao
            WHERE entidade = :entidade"""
        data = self._db.execute_query_first_result(sql, entidade=entidade)

        return data['data_ultima_integracao'] if data else None


    def listar_entidades_pendentes_integracao(self):
        sql = """SELECT
                entidade,
                coalesce(data_ultima_integracao, created_at) data_ultima_integracao
            FROM util.entidades_integracao
            """
        entidades = self._db.execute_query(sql)

        return { entidade['entidade'] :entidade['data_ultima_integracao'] for entidade in entidades }


    def listar_dados_exclusao(self, pk: str, entidade: str, data_ultima_integracao: datetime):
        sql = f"""SELECT
	        (oldvalue->>'{pk}')::uuid as id
        FROM ns.rastros
        WHERE
	        operacao= 'DELETE' AND
	        concat(schema,'.',tabela) = '{entidade}' AND
	        data >= :data
            """
        dados = self._db.execute_query(sql, data=data_ultima_integracao)

        return [ str(valor['id']) if valor['id'] is not None else None for valor in dados ]


    def listar_dados_alteracao(self, pk: str, entidade: str, data_ultima_integracao: datetime):
        sql = f"""SELECT
	        (newvalue->>'{pk}')::uuid as id
        FROM ns.rastros
        WHERE
	        operacao in ('INSERT','UPDATE') AND
	        concat(schema,'.',tabela) = '{entidade}' AND
	        data >= :data
            """
        dados = self._db.execute_query(sql, data=data_ultima_integracao)

        return [ str(valor['id']) if valor['id'] is not None else None for valor in dados ]


    def atualiza_ultima_integracao(self, entidade: str, filtros : list):
        sql = """INSERT INTO util.entidades_integracao(entidade, filtros_integracao, created_at)
        VALUES (:entidade, :filtros, current_timestamp AT TIME ZONE 'America/Sao_Paulo')
        ON CONFLICT (entidade) DO
        UPDATE
        SET
            data_ultima_integracao = current_timestamp AT TIME ZONE 'America/Sao_Paulo'
        WHERE
            excluded.entidade=:entidade_filtro"""

        _filtros = json_dumps(filtros)

        self._db.execute(sql, entidade=entidade, filtros=_filtros, entidade_filtro=entidade)


    def atualiza_data_ultima_integracao(self, entidade: str, data: datetime ,filtros: list):
        sql = """INSERT INTO util.entidades_integracao(entidade, filtros_integracao, created_at)
        VALUES (:entidade, :filtros, :data AT TIME ZONE 'America/Sao_Paulo')
        ON CONFLICT (entidade) DO
        UPDATE
        SET
            data_ultima_integracao = :data AT TIME ZONE 'America/Sao_Paulo'
        WHERE
            excluded.entidade=:entidade_filtro"""

        _filtros = json_dumps(filtros)

        self._db.execute(sql, entidade=entidade, data=data ,filtros=_filtros, entidade_filtro=entidade)


    def registra_entidade_integracao(self, entidade: str):
        sql = """INSERT INTO util.entidades_integracao(entidade, created_at)
        VALUES (:entidade, current_timestamp AT TIME ZONE 'America/Sao_Paulo')
        ON CONFLICT (entidade) DO NOTHING;"""

        self._db.execute(sql, entidade=entidade)


    def integracao_configurada(self) -> bool:
        sql = """SELECT
                count(*)
            FROM ns.configuracoes
            WHERE string_ini = 'API_TOKEN_SINCRONIA'"""
        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def symmetrics_instalado(self) -> bool:
        sql = """SELECT
            count(*)
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'sym_node'"""

        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def existem_nodes_symmetrics_ativos(self) -> bool:
        sql = """SELECT
            count(*)
            FROM sym_node
            WHERE sync_enabled = 1"""

        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def symmetrics_local_ativo(self) -> bool:
        sql = """SELECT
                count(*)
            FROM ns.configuracoes
            WHERE string_ini = ('FLAG_SINCRONIA_ATIVADA') and lower(valor) = 'true'"""

        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def desabilitar_symmetrics_local(self):
        sql = """UPDATE ns.configuracoes
            SET valor = false
            WHERE string_ini = ('FLAG_SINCRONIA_ATIVADA') """

        self._db.execute(sql)

    def habilitar_symmetrics_local(self):
        sql = """UPDATE ns.configuracoes
            SET valor = true
            WHERE string_ini = ('FLAG_SINCRONIA_ATIVADA') """

        self._db.execute(sql)


    def desabilitar_nodes_symmetrics(self):
        sql = "UPDATE sym_node SET sync_enabled=0"

        self._db.execute(sql)


    def habilitar_nodes_symmetrics(self):
        sql = "UPDATE sym_node SET sync_enabled=1"

        self._db.execute(sql)


    def recuperar_token(self) -> str:
        sql = """SELECT
                valor
            FROM ns.configuracoes
            WHERE string_ini = 'API_TOKEN_SINCRONIA'"""
        data = self._db.execute_query_first_result(sql)

        return data["valor"]


    def registra_token_tenant(self, token: str):
        sql = """INSERT INTO ns.configuracoes(valor, string_ini)
        VALUES (:valor, 'API_TOKEN_SINCRONIA');"""

        self._db.execute(sql, valor=token)


    def remove_token_tenant(self):
        sql = """DELETE FROM ns.configuracoes WHERE string_ini = 'API_TOKEN_SINCRONIA';"""

        self._db.execute(sql)


    def listar_grupos_empresariais(self, grupos: List[str] = None):
        sql = """SELECT
                grupoempresarial id,
                codigo,
                descricao
            FROM ns.gruposempresariais"""

        if grupos:
            sql = sql + """
            WHERE codigo in :grupos"""

        grupos = self._db.execute_query(sql, grupos=tuple(grupos) if grupos else None)

        return grupos


    def registrar_grupos_empresariais(self, grupos_ids: List[str]):

        # Criar a consulta SQL com múltiplos valores
        values_placeholder = ", ".join(["(:id_{0})".format(i) for i in range(len(grupos_ids))])

        sql = f"""INSERT INTO util.grupos_empresariais_integracao(grupoempresarial)
        VALUES {values_placeholder}
        ON CONFLICT (grupoempresarial) DO UPDATE
        SET ativo = true;"""

        # Criar o dicionário de parâmetros
        params = {f"id_{i}": id_ for i, id_ in enumerate(grupos_ids)}

        rowcount, _ = self._db.execute(sql, **params)

        if rowcount!=len(grupos_ids):
            raise Exception(
                "Erro ao registrar grupos empresariais no banco de dados"
            )


    def existem_grupos_empresariais_integracao_ativos(self):
        sql = """SELECT
                count(*)
            FROM util.grupos_empresariais_integracao WHERE ativo = true"""

        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def listar_grupos_empresariais_integracao(self):
        sql = """SELECT
                gru.grupoempresarial as id,
                gru.codigo,
                gru.descricao,
                coalesce(gei.ativo, false) ativo
            FROM ns.gruposempresariais gru
            LEFT JOIN util.grupos_empresariais_integracao gei
            ON gei.grupoempresarial = gru.grupoempresarial"""

        return self._db.execute_query(sql)


    def desativar_grupos_empresariais(self, grupos_ids: List[str]):
        sql = """UPDATE util.grupos_empresariais_integracao
        SET ativo = false
        WHERE grupoempresarial in :grupos"""
        self._db.execute(sql, grupos=tuple(grupos_ids))


    def alterar_status_grupo_empresarial(self, grupo: str, ativo: bool):
        sql = """UPDATE util.grupos_empresariais_integracao
        SET ativo = :ativo
        WHERE grupoempresarial = :grupo"""
        self._db.execute(sql, ativo=ativo, grupo=grupo)


    def listar_dados_particionamento(self):
        sql = """SELECT
        gru.grupoempresarial,
        emp.empresa,
        est.estabelecimento
        FROM util.grupos_empresariais_integracao gei
        JOIN ns.gruposempresariais gru on ( gru.grupoempresarial =  gei.grupoempresarial )
        JOIN ns.empresas emp on ( emp.grupoempresarial = gru.grupoempresarial )
        JOIN ns.estabelecimentos est on (est.empresa = emp.empresa)
        WHERE gei.ativo"""

        return self._db.execute_query(sql)


    def listar_execucoes(self):
        sql = """SELECT
        jt.jobtype,
        jt.codigo,
        jt.descricao,
        j.job,
        j.entrada,
        j.saida,
        j.status,
        j.progresso,
        j.enfileiramento,
        j.inicioexecucao,
        j.fimexecucao,
        j.fimexecucao - j.inicioexecucao duracao
        FROM util.jobtypes jt
        JOIN util.jobs j ON (j.jobtype = jt.jobtype )
        WHERE jt.codigo='INTEGRACAO_APIS'
        order by inicioexecucao desc nulls last"""

        return self._db.execute_query(sql)


    def listar_logs_execucoes(self, job):
        sql = """SELECT
        registroexecucaojob,
        job,
        datahora,
        tipo,
        mensagem
        FROM
        util.registroexecucaojobs
        WHERE job = :job
        ORDER BY datahora ASC"""

        return self._db.execute_query(sql, job=job)


    def listar_blobs_entidade(self, id_field: str, field: str, entidade: str, ids: list):
        """
        Lista blobs (fotos) de uma entidade para os ids informados.
        """
        if not ids:
            return []

        # Monta a lista de placeholders para os parâmetros
        sql = f"""
        SELECT
            {id_field} as id,
            {field} as  _blob
        FROM
            {entidade}
        WHERE
            {id_field} IN :ids
        """
        _data = self._db.execute_query(sql, ids=tuple(ids))
        result = []
        for row in _data:
            foto = row.get("_blob")

            if foto is not None:
                hash_value = hashlib.sha256(foto).hexdigest()
            else:
                hash_value = None

            result.append({
                "id": str(row["id"]),
                "hash": hash_value,
                "blob": foto
            })
        return result


    def recuperar_configuracao_ambiente(self):
        sql = """SELECT
                valor
            FROM ns.configuracoes
            WHERE string_ini = 'INTEGRACAO_APIS_ENV'"""
        data = self._db.execute_query_first_result(sql)

        return data["valor"].upper() if data else None
