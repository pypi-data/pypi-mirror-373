from typing import List, Dict, Callable, Iterator

from collections import defaultdict

import os

import copy

import hashlib

import datetime

from zoneinfo import ZoneInfo

import colorama

import tzdata

from nsj_gcf_utils.json_util import json_loads, json_dumps, JsonLoadException

from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_list_field import DTOListField
from nsj_rest_lib.exception import AfterRecordNotFoundException

from nsj_integracao_api_client.service.integrador_cfg import (
    _entidades_filtros_integracao, _entidades_integracao, _entidades_particionadas_por_empresa,
    _entidades_particionadas_por_estabelecimento, _entidades_particionadas_por_grupo,
    _cfg_filtros_to_dto_filtro, _ignorar_integridade, _entidades_blob,
    medir_tempo, Environment, TAMANHO_PAGINA, _E_CHECK_INT,
    TipoVerificacaoIntegridade
)

from nsj_integracao_api_client.infra.api_client import ApiClient

from nsj_integracao_api_client.infra.token_service import TokenService

from nsj_integracao_api_client.infra.injector_factory import InjectorFactory

from nsj_integracao_api_client.dao.integracao import IntegracaoDAO

from nsj_integracao_api_client.infra.debug_utils import DebugUtils as _du

from nsj_integracao_api_entidades.nsj_rest_lib_extensions.dao.integridade_dao import IntegridadeDAO


colorama.init(autoreset=True)

out_func: Callable = print

_is_console = False


class IntegradorService():

    _injector : InjectorFactory = None

    _dao_intg: IntegracaoDAO = None

    _tz_br: ZoneInfo = None

    _token_service: TokenService = None

    _api_client: ApiClient = None

    _api_key: str = None

    _tenant: int = None

    # Caso se deseje usar um tenant diferente do especificado no token
    _forced_tenant: int = None

    _filtros_particionamento: list = None

    _save_point: dict = {}

    _ignored_fields : list = ["tenant", "lastupdate"]

    _detalhar_diferencas: bool

    _trace: bool

    _interromper_execucao: bool

    _em_execucao: bool

    _menos_log: bool

    _adicionar_data_log: bool

    def __init__(
        self,
        injector: InjectorFactory,
        log,
        env: Environment = Environment.PROD,
        forced_tenant: int = None,
        menos_log: bool = False,
        adicionar_data_log: bool = False
    ):
        self._injector = injector
        env_cfg = self._integracao_dao().recuperar_configuracao_ambiente()
        env = Environment(env_cfg) if env_cfg else env
        self._logger = log
        self._forced_tenant = forced_tenant
        self._tz_br = ZoneInfo("America/Sao_Paulo")
        self._detalhar_diferencas = False
        self._trace = False
        self._api_client = ApiClient(env)
        self._token_service = TokenService()
        self._interromper_execucao = False
        self._em_execucao = False
        self._menos_log = menos_log
        self._adicionar_data_log = adicionar_data_log


    def _log(self, msg):
        if self._adicionar_data_log and msg.replace("\n", "").replace("\r", "") != "":
            msg = f"[{datetime.datetime.now(self._tz_br).strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        self._logger.mensagem(msg)


    def _processa_mensagens(self, msgs: Iterator[str]):
        for msg in msgs:
            if not self._menos_log:
                self._log(msg)


    def _carregar_savepoint(self):
        try:
            with open('savepoint.json', 'r', encoding='utf-8') as f:
                self._save_point = json_loads(f.read())
                entidade_salva = list(self._save_point.keys())[0]
                self._log(f"Savepoint carregado para : {entidade_salva }")
        except FileNotFoundError:
            self._save_point = {}


    def _trace_check(self, filename, content):

        _du.conditional_trace(
            condition=_E_CHECK_INT or self._trace,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )


    def _detail_check(self, filename, content):

        _du.conditional_trace(
            condition=_E_CHECK_INT or self._detalhar_diferencas,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )


    def _fields_to_load(self, dto_class) -> dict:

        fields = {}
        fields.setdefault("root", set(dto_class.fields_map.keys()))

        for _related_entity, _related_list_fields in dto_class.list_fields_map.items():
            fields["root"].add(_related_entity)
            fields.setdefault(_related_entity, set())
            _related_fields = _related_list_fields.dto_type.fields_map.keys()
            for _related_field in _related_fields:
                fields["root"].add(f"{_related_entity}.{_related_field}")
                fields[_related_entity].add(_related_field)

        return fields


    def _integracao_dao(self):
        if self._dao_intg is None:
            self._dao_intg = self._injector.integracao_dao()
        return self._dao_intg


    @property
    def api_key(self):

        if self._api_key is None:
            self._api_key = self._integracao_dao().recuperar_token()

        return self._api_key


    @property
    def tenant(self):

        if self._forced_tenant is not None:
            return self._forced_tenant

        if self._tenant is None:
            decoded_token = self._token_service.decode_token(self.api_key)
            self._tenant = decoded_token["tenant_id"]

        return self._tenant


    def _integracao_foi_configurada(self):
        return self._integracao_dao().integracao_configurada()


    def _validar_grupos_empresariais(self, grupos) -> List[Dict[str, str]]:

        grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais(grupos)
        _cods = [grupo['codigo'] for grupo in grupos_cadastrados]
        _grupos_faltantes = [grupo for grupo in grupos if grupo not in _cods]
        assert len(_grupos_faltantes)==0, f"Grupo(s) '{','.join(_grupos_faltantes)}' não encontrado(s)."
        return grupos_cadastrados


    def registrar_entidades_integracao(self):
        for entidade in _entidades_integracao:

            self._integracao_dao().registra_entidade_integracao(entidade)

            _dto = self._injector.dto_for(entidade, False)

            for field in _dto.list_fields_map.values():
                _sub_entity = field.entity_type.table_name
                self._integracao_dao().registra_entidade_integracao(_sub_entity)


    def executar_instalacao(self, chave_ativacao: str, grupos: List[str]):

        assert chave_ativacao, "Chave de ativação não pode ser vazia."
        self._log(f"Executando instalação com a chave de ativação: {chave_ativacao}")

        assert not self._integracao_foi_configurada(), "Integração já instalada anteriormente."
        _token: str = self._api_client.gerar_token_tenant(chave_ativacao)
        decoded_token = self._token_service.decode_token(_token)

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [str(grupo['id']) for grupo in grupos_cadastrados]

        try:
            self._integracao_dao().begin()

            self._integracao_dao().registrar_grupos_empresariais(_ids)

            self._integracao_dao().registra_token_tenant(_token)

            self.registrar_entidades_integracao()

            self._integracao_dao().commit()

            self._log(f"Instalação efetuada com sucesso para o tenant '{decoded_token['tenant_id']}'.")
        except Exception:
            self._integracao_dao().rollback()
            raise


    def ativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [grupo['id'] for grupo in grupos_cadastrados]

        self._integracao_dao().registrar_grupos_empresariais(_ids)

        if grupos:
            self._log(f"Grupos empresariais ativados: '{','.join(grupos)}'.")
        else:
            _codigos  = [grupo['codigo'] for grupo in grupos_cadastrados]
            self._log(f"Grupos empresariais ativados: '{','.join(_codigos)}'.")


    def desativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"
        assert grupos, "Grupos não podem ser vazios!"

        grupos_cadastrados = self._validar_grupos_empresariais(grupos)

        _ids  = [grupo['id'] for grupo in grupos_cadastrados]

        self._integracao_dao().desativar_grupos_empresariais(_ids)

        self._log(f"Grupos empresariais desativados: '{','.join(grupos)}'.")


    def _filtro_particionamento_de(self, entidade: str):

        if self._filtros_particionamento is None:
            _dados_part = self._integracao_dao().listar_dados_particionamento()

            assert _dados_part, "Não existem entidades empresariais cadastradas para integração!"

            self._filtros_particionamento = [
                {'grupoempresarial' : ",".join(list(map(lambda i: str(i["grupoempresarial"]), _dados_part)))},
                {'empresa' : ",".join(list(map(lambda i: str(i["empresa"]), _dados_part)))},
                {'estabelecimento' : ",".join(list(map(lambda i: str(i["estabelecimento"]), _dados_part)))}
            ]

        if entidade in _entidades_particionadas_por_grupo:
            return  self._filtros_particionamento[0]

        if entidade in _entidades_particionadas_por_empresa:
            return self._filtros_particionamento[1]

        if entidade in _entidades_particionadas_por_estabelecimento:
            return self._filtros_particionamento[2]

        return {}


    def _filtros_integracao_cfg(self, entidade: str):

        _filtro_salvo = self._integracao_dao().filtros_integracao_entidade(entidade)

        if not isinstance(_filtro_salvo, list):
            self._log(f"O filtro salvo para a entidade '{entidade}' deve ser uma lista, {_filtro_salvo} fornecido.")
            _filtro_salvo = []

        _filtros = (
            _entidades_filtros_integracao[entidade] +
            _filtro_salvo
        )
        #Garante unicidade do campo no filtro
        dict_filtros = {}
        for _item in _filtros:
            if "campo" in _item and "valor" in _item and "operador" in _item:
                dict_filtros[_item['campo']] = copy.copy(_item)
            else:
                self._log(f"O filtro salvo para a entidade '{entidade}' deve conter campo,valor e operador': {_item} fornecido.")

        return list(dict_filtros.values())


    def _dto_to_api(
        self,
        campos: Dict[str, List[str]],
        data: List[DTOBase]
    ) -> List[dict]:
        # Converte os objetos DTO para dicionários e adiciona o tenant
        transformed_data = []
        for dto in data:
            dto.tenant = self.tenant
            dto_dict = dto.convert_to_dict(campos)

            # Implementado devido a dualidade de conversão de campos json na API que podem ser convertidos com str/dict

            if "created_by" in dto_dict and not dto_dict["created_by"] is None:
                if not isinstance(dto_dict["created_by"], dict):
                    try:
                        _value_dict = json_loads(dto_dict["created_by"])
                        dto_dict["created_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dto_dict["created_by"] = {"id": dto_dict["created_by"]}

            if "updated_by" in dto_dict and not dto_dict["updated_by"] is None:
                if not isinstance(dto_dict["updated_by"], dict):
                    try:
                        _value_dict = json_loads(dto_dict["updated_by"])
                        dto_dict["updated_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dto_dict["updated_by"] = {"id": dto_dict["updated_by"]}


            transformed_data.append(dto_dict)

        return transformed_data


    def _save_point_for(self, tabela: str):
        return self._save_point.get(tabela, None)


    def _do_save_point(self, tabela: str, chave):
        self._save_point[tabela] = chave
        with open('savepoint.json', 'w', encoding='utf-8') as f:
            f.write(f'{{ "{tabela}": "{chave}" }} ' if chave else f'{{ "{tabela}": null }} ')


    def _save_point_clear(self):
        self._save_point.clear()
        if os.path.exists('savepoint.json'):
            os.remove('savepoint.json')


    def interromper_execucao(self):
        self._interromper_execucao = True
        self._em_execucao = False


    def em_execucao(self):
        return self._em_execucao


    def _atualiza_ultima_integracao(self, entidade: str, filtros : list):
        self._integracao_dao().atualiza_ultima_integracao(entidade, filtros)

        _dto = self._injector.dto_for(entidade, False)

        for field in _dto.list_fields_map.values():
            _sub_entity = field.entity_type.table_name
            self._integracao_dao().atualiza_ultima_integracao(_sub_entity, [])


    def _atualiza_data_ultima_integracao(self, entidade: str, data: datetime.datetime, filtros: list):
        self._integracao_dao().atualiza_data_ultima_integracao(entidade, data, filtros)

        _dto = self._injector.dto_for(entidade, False)

        for field in _dto.list_fields_map.values():
            _sub_entity = field.entity_type.table_name
            self._integracao_dao().atualiza_data_ultima_integracao(_sub_entity, data, [])


    def _enviar_dados(self, dict_data: list, entidade: str, parar_caso_erros: bool = False) -> list:
        _erros = []
        try:
            # Tenta o envio em bloco
            self._api_client.enviar_dados(dict_data, entidade, self.api_key)
        except Exception:
            # Se o envio em bloco falhar, tenta o envio item por item
            for _item in dict_data:
                try:
                    self._api_client.enviar_dados([_item], entidade, self.api_key)
                except Exception as e:
                    if parar_caso_erros:
                        raise e
                    else:
                        self._log("")
                        self._log(f"\n{'-'*80}\nErro:\n{str(e)}\n{'-'*80 if _item == dict_data[-1] else ''}")
                        self._log("")
                        _erros.append(e)
        return _erros


    def _apagar_dados(self, dict_data: list, entidade: str, parar_caso_erros: bool = False) -> list:
        _erros = []
        try:
            # Tenta o envio em bloco
            mensagens = self._api_client.apagar_dados(dict_data, entidade, self.api_key, self.tenant)
            self._processa_mensagens(mensagens)
        except Exception:
            # Se o envio em bloco falhar, tenta o envio item por item
            for _item in dict_data:
                try:
                    mensagens = self._api_client.apagar_dados([_item], entidade, self.api_key, self.tenant)
                    self._processa_mensagens(mensagens)
                except Exception as e:
                    if parar_caso_erros:
                        raise e
                    else:
                        self._log("")
                        self._log(f"\n{'-'*80}\nErro:\n{str(e)}\n{'-'*80 if _item == dict_data[-1] else ''}")
                        self._log("")
                        _erros.append(e)

        return _erros


    def _enviar_blobs(self, ids: list, files: list ,entidade: str, campo: str, parar_caso_erros: bool = False):
        _erros = []
        try:
            # Tenta o envio em bloco
            self._api_client.enviar_blobs(ids, files ,entidade, campo, self.tenant, self.api_key)
        except Exception:
            # Se o envio em bloco falhar, tenta o envio item por item
            for i, file in enumerate(files):
                try:
                    self._api_client.enviar_blobs([ids[i]], [file] ,entidade, campo, self.tenant, self.api_key)
                except Exception as e:
                    if parar_caso_erros:
                        raise e
                    else:
                        self._log("")
                        self._log(f"\n{'-'*80}\nErro:\n{str(e)}\n{'-'*80}")
                        self._log("")
                        _erros.append(e)

        return _erros


    def _processar_blobs(self, entidade: str, service, dict_data: list, avaliar_diferencas: bool = True, parar_caso_erros: bool = False):

        if entidade in _entidades_blob:

            if service is None:
                service = self._injector.service_for(entidade, True)

            _campos = _entidades_blob[entidade]
            _ids = [i['id'] for i in dict_data]
            _pk_banco = service._entity_class.pk_field

            self._log(f"Verificando se houve alterações nos blobs da entidade {entidade}.")

            for _campo in _campos:

                _ids_blobs = []
                _file_blobs = []

                if avaliar_diferencas:
                    _ids_to_send_blob = self._api_client.consultar_hash_blob(_ids, entidade, _campo, self.tenant, self.api_key)

                    _hashes_blob_remoto = _ids_to_send_blob['result']

                    _hashes_blob_local = self._integracao_dao().listar_blobs_entidade(_pk_banco, _campo, entidade, _ids)

                    # comparar md5
                    for blob_local in _hashes_blob_local:
                        id_local = blob_local['id']
                        hash_local = blob_local['hash']
                        # Procura o hash remoto correspondente
                        hash_remoto = next((item['hash'] for item in _hashes_blob_remoto if item['id'] == id_local), None)
                        if hash_remoto != hash_local and blob_local['blob'] is not None:
                            _ids_blobs.append(blob_local['id'])
                            _file_blobs.append(('files', (blob_local['id'], blob_local['blob'], 'application/octet-stream')))
                else:
                    _hashes_blob_local = self._integracao_dao().listar_blobs_entidade(_pk_banco, _campo, entidade, _ids)
                    for blob_local in _hashes_blob_local:
                        if blob_local['blob'] is not None:
                            _ids_blobs.append(blob_local['id'])
                            _file_blobs.append(('files', (blob_local['id'], blob_local['blob'], 'application/octet-stream')))


                self._log(f"Enviando blobs do campo {_campo} para a api.")
                if _ids_blobs:
                    self._enviar_blobs(
                        _ids_blobs,
                        _file_blobs,
                        entidade,
                        _campo,
                        parar_caso_erros
                    )


    @medir_tempo("Carga inicial")
    def executar_carga_inicial(self, entidades: list, parar_caso_erros: bool = False):
        self._interromper_execucao = False
        self._em_execucao = True

        try:
            assert self._integracao_foi_configurada(), "Integração não configurada!"

            _dao = self._integracao_dao()

            assert _dao.existem_grupos_empresariais_integracao_ativos(), "Nenhum grupo empresarial ativo para integração."

            self._log(f"Executando carga inicial para o Tenant: {self.tenant} .")
            self._log(f"{len(_entidades_integracao)} entidades para processar.")

            entidades_carga_inicial = copy.copy(_entidades_integracao)

            # Remover entidades que nao devem ser processadas
            if entidades:
                for entidade in entidades:
                    assert entidade in _entidades_integracao, f"Entidade '{entidade}' não consta como entidade para integração!"

                for entidade in _entidades_integracao:
                    if not entidade in entidades:
                        entidades_carga_inicial.remove(entidade)

            _erros_envio = []

            # Remover entidades que ja foram processadas
            if not entidades:
                self._carregar_savepoint()
                if self._save_point:
                    for entidade in _entidades_integracao:
                        if not entidade in self._save_point:
                            entidades_carga_inicial.remove(entidade)
                        else:
                            break

            for entidade in entidades_carga_inicial:

                # if not entidade in ['persona.adiantamentosavulsos','persona.trabalhadores']:
                #     continue

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _idx = _entidades_integracao.index(entidade) + 1
                self._log(f"Efetuando carga {entidade}, {_idx} de {len(_entidades_integracao)}.")
                _count = 0

                # Carregar dados paginados para integrar
                service = self._injector.service_for(entidade, True)
                fields = self._fields_to_load(service._dto_class)
                _filtros_particionamento = self._filtro_particionamento_de(entidade)
                _filtros_integracao_cfg = self._filtros_integracao_cfg(entidade)
                filters = _filtros_particionamento | _cfg_filtros_to_dto_filtro(_filtros_integracao_cfg)
                search_query = None

                #pagina = 0
                self._log("Extraindo dados para carga.")
                while True:

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    current_after = self._save_point_for(entidade)
                    _data = service.list(
                            current_after,
                            TAMANHO_PAGINA,
                            fields,
                            None,
                            filters,
                            search_query=search_query,
                        )

                    _count = _count + len(_data)

                    if len(_data)==0:
                        if current_after is None:
                            self._log("Sem dados para transferir, indo adiante.")
                        else:
                            self._log("Entidade integrada com sucesso.")
                        break

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    self._log(f"{_count} registro(s).")

                    dict_data = self._dto_to_api(fields, _data)

                    self._log("Enviando dados para a api.")
                    _erros_envio += self._enviar_dados(dict_data, entidade, parar_caso_erros)

                    self._processar_blobs(entidade, service, dict_data, False, parar_caso_erros)

                    # Aponta a leitura para a próxima página
                    _last = _data[-1]
                    self._do_save_point(entidade, getattr(_last, _last.pk_field))

                self._atualiza_ultima_integracao(entidade, _filtros_integracao_cfg)
                self._save_point_clear()

            self._log(self._color("Carga inicial finalizada com sucesso!", "92", _is_console))

            if _erros_envio:
                self._log(self._color("Ocorreram erros que foram ignorados durante o processo, verifique:", 91, _is_console))
                self._log("")
                self._log("\n"+("-"*80)+"\n"+self._color("\n".join(str(e)+ "\n" + "-"*80 for e in _erros_envio), 91, _is_console))

        finally:
            self._em_execucao = False


    @medir_tempo("Integração")
    def executar_integracao_old(self):
        self._interromper_execucao = False
        self._em_execucao = True

        try:
            assert self._integracao_foi_configurada(), "Integração não configurada!"

            _dao = self._integracao_dao()

            assert _dao.existem_grupos_empresariais_integracao_ativos(), "Nenhum grupo empresarial ativo para integração."

            self._log(f"Executando integração para o Tenant: {self.tenant} .")

            entidades_pendentes_bd = _dao.listar_entidades_pendentes_integracao()

            # Não filtrar entidades filhas
            entidades_pendentes = {entidade: entidades_pendentes_bd[entidade] for entidade in _entidades_integracao if entidade in entidades_pendentes_bd.keys()}

            self._log(f"{len(entidades_pendentes)} entidades para processar." if entidades_pendentes else "Nenhuma entidade para processar.")
            _resumo = {}

            self._integracao_dir = f"integracao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            for entidade, data_ultima_integracao in entidades_pendentes.items():


                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _idx = list(entidades_pendentes.keys()).index(entidade) + 1
                self._log(f"Integrando {entidade}, {_idx} de {len(entidades_pendentes)}.")
                _count = 0

                # Carregar dados paginados para integrar
                service = self._injector.service_for(entidade, True)
                current_after = None
                fields = self._fields_to_load(service._dto_class) #tornar publico
                _filtros_particionamento = self._filtro_particionamento_de(entidade)
                _filtros_integracao_cfg = self._filtros_integracao_cfg(entidade)
                filters = _filtros_particionamento | _cfg_filtros_to_dto_filtro(_filtros_integracao_cfg)
                search_query = None

                # Dados excluidos apos data_ultima_integracao
                _coluna_id = service._dto_class.fields_map[service._dto_class.pk_field].entity_field
                para_apagar = _dao.listar_dados_exclusao(_coluna_id, entidade, data_ultima_integracao)
                if para_apagar:
                    for i in range(0, len(para_apagar), TAMANHO_PAGINA):
                        bloco_para_apagar = para_apagar[i:i+TAMANHO_PAGINA]
                        _resumo[entidade] = _resumo.get(entidade, 0) + len(bloco_para_apagar)
                        mensagens = self._api_client.apagar_dados(bloco_para_apagar, entidade, self.api_key, self.tenant)
                        self._processa_mensagens(mensagens)

                # Dados alterados apos data_ultima_integracao
                filtro_atualizacao = filters.copy() if filters else {}
                filtro_atualizacao['lastupdate'] = data_ultima_integracao
                while True:

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    _data = service.list(
                            current_after,
                            TAMANHO_PAGINA,
                            fields,
                            None,
                            filtro_atualizacao,
                            search_query=search_query,
                        )

                    _count = _count + len(_data)

                    if len(_data)==0:
                        break

                    self._log(f"{_count} registro(s).")
                    _resumo[entidade] = _resumo.get(entidade, 0) + _count

                    # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                    dict_data = self._dto_to_api(fields, _data)

                    # Mandar a bagatela por apis
                    self._api_client.enviar_dados(dict_data, entidade, self.api_key)

                    self._processar_blobs(entidade, service, dict_data)

                    # Aponta a leitura para a próxima página
                    _last = _data[-1]
                    current_after = getattr(_last, _last.pk_field)


                # Carrega os objetos pais a partir dos dados modificados nas entidades filhas
                lista_ids_entidades_atualizar = []
                for _chave, _campo_lista in service._dto_class.list_fields_map.items():
                    #_sub_dto      = _campo_lista.dto_type
                    _sub_entidade = _campo_lista.entity_type.table_name
                    _sub_data_ultima_integracao = entidades_pendentes_bd[_sub_entidade]
                    _campo_id_pai = _campo_lista.related_entity_field

                    #_coluna_id_filho = _sub_dto.fields_map[_sub_dto.pk_field].entity_field
                    para_apagar    = _dao.listar_dados_exclusao(_campo_id_pai, _sub_entidade, _sub_data_ultima_integracao)
                    para_atualizar = _dao.listar_dados_alteracao(_campo_id_pai, _sub_entidade, _sub_data_ultima_integracao)

                    lista_ids_entidades_atualizar = lista_ids_entidades_atualizar + para_apagar + para_atualizar


                if lista_ids_entidades_atualizar:

                    current_after = None
                    filtro_atualizacao = filters.copy() if filters else {}
                    filtro_atualizacao[_coluna_id] = ",".join([str(id) for id in lista_ids_entidades_atualizar if id is not None])

                    while True:

                        if self._interromper_execucao:
                            self._log("Processo interrompido pelo usuário.")
                            return

                        _data = service.list(
                                current_after,
                                TAMANHO_PAGINA,
                                fields,
                                None,
                                filtro_atualizacao,
                                search_query=search_query,
                            )

                        _count = _count + len(_data)

                        if len(_data)==0:
                            break

                        self._log(f"{_count} registro(s).")
                        _resumo[entidade] = _resumo.get(entidade, 0) + _count

                        # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                        dict_data = self._dto_to_api(fields, _data)

                        # Mandar a bagatela por apis
                        self._api_client.enviar_dados(dict_data, entidade, self.api_key)

                        # Aponta a leitura para a próxima página
                        _last = _data[-1]
                        current_after = getattr(_last, _last.pk_field)


                self._atualiza_ultima_integracao(entidade, _filtros_integracao_cfg)

            self._log("")
            self._log(self._color("Integração finalizada com sucesso!", 92, _is_console))
            if _resumo:
                self._log("")
                self._log(self._color(f"Resumo da integração: {', '.join(f'{k}: {v}' for k, v in _resumo.items())}", 92, _is_console))

        finally:
            self._em_execucao = False


    @medir_tempo("Integração")
    def executar_integracao(self, parar_caso_erros: bool = False):
        self._interromper_execucao = False
        self._em_execucao = True

        try:
            assert self._integracao_foi_configurada(), "Integração não configurada!"

            _dao = self._integracao_dao()

            assert _dao.existem_grupos_empresariais_integracao_ativos(), "Nenhum grupo empresarial ativo para integração."

            self._log(f"Executando integração para o Tenant: {self.tenant} .")

            entidades_pendentes_bd = _dao.listar_entidades_pendentes_integracao()

            # Não filtrar entidades filhas
            entidades_pendentes = {entidade: entidades_pendentes_bd[entidade] for entidade in _entidades_integracao if entidade in entidades_pendentes_bd.keys()}

            self._log(f"{len(entidades_pendentes)} entidades para processar." if entidades_pendentes else "Nenhuma entidade para processar.")
            _resumo = {}

            if not entidades_pendentes:
                return

            self._integracao_dir = f"integracao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            _data_integracao: Dict[str, datetime.datetime] = {}

            _total_passos = len(entidades_pendentes) * 2
            _idx = 0

            _erros_envio = []

            # Processa exclusões gerais
            self._log("")
            self._log("Iniciando integração das exclusões pendentes.")
            for entidade, data_ultima_integracao in reversed(entidades_pendentes.items()):

                # if not entidade in ['ns.enderecos']:
                #     continue

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _idx += 1
                if not self._menos_log:
                    self._log(f"{entidade}, {_idx} de {_total_passos}.")

                service = self._injector.service_for(entidade, True)

                _data_integracao[entidade] = datetime.datetime.now(self._tz_br)

                _coluna_id = service._dto_class.fields_map[service._dto_class.pk_field].entity_field
                # TODO: ajustar para o horário do servidor. Fiz esse recursos devido a diferenã de timestamp entre o rastro e o registro,
                #  o que fazia com que o rastros ficasse atrasados em relação aos registros e consequentemente não houvesse exclusão.
                data_ultima_integracao_ajustada = data_ultima_integracao - datetime.timedelta(hours=6)
                #print(data_ultima_integracao_ajustada)
                para_apagar = _dao.listar_dados_exclusao(_coluna_id, entidade, data_ultima_integracao_ajustada)
                if para_apagar:

                    for i in range(0, len(para_apagar), TAMANHO_PAGINA):
                        bloco_ids = para_apagar[i:i+TAMANHO_PAGINA]
                        _resumo[entidade] = _resumo.get(entidade, 0) + len(bloco_ids)
                        _erros_envio += self._apagar_dados(bloco_ids, entidade, parar_caso_erros)

                    if not self._menos_log:
                        self._log("Entidade integrada com sucesso.")
                    self._log(f"{entidade}: {len(para_apagar)} registro(s).")
                else:
                    if not self._menos_log:
                        self._log("Sem dados para atualizar, indo adiante.")



            # Processa upserts
            self._log("")
            self._log("Iniciando integração das atualizações pendentes.")
            for entidade, data_ultima_integracao in entidades_pendentes.items():

                # if not entidade in ['ns.enderecos']:
                #     continue

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _idx += 1
                if not self._menos_log:
                    self._log(f"{entidade}, {_idx} de {_total_passos}.")
                _count = 0

                # Carregar dados paginados para integrar
                service = self._injector.service_for(entidade, True)
                current_after = None
                fields = self._fields_to_load(service._dto_class) #tornar publico
                _filtros_particionamento = self._filtro_particionamento_de(entidade)
                _filtros_integracao_cfg = self._filtros_integracao_cfg(entidade)
                filters = _filtros_particionamento | _cfg_filtros_to_dto_filtro(_filtros_integracao_cfg)
                search_query = None


                # Dados alterados apos data_ultima_integracao
                filtro_atualizacao = filters.copy() if filters else {}
                filtro_atualizacao['lastupdate'] = data_ultima_integracao
                while True:

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    _data = service.list(
                            current_after,
                            TAMANHO_PAGINA,
                            fields,
                            None,
                            filtro_atualizacao,
                            search_query=search_query,
                        )

                    _count = _count + len(_data)

                    if len(_data)==0:
                        break

                    # if not self._menos_log:
                    #     self._log(f"{entidade}: {_count} registro(s)")

                    _resumo[entidade] = _resumo.get(entidade, 0) + _count

                    # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                    dict_data = self._dto_to_api(fields, _data)

                    # Mandar a bagatela por apis
                    _erros_envio += self._enviar_dados(dict_data, entidade, parar_caso_erros)

                    self._processar_blobs(entidade, service, dict_data, True, parar_caso_erros)

                    # Aponta a leitura para a próxima página
                    _last = _data[-1]
                    current_after = getattr(_last, _last.pk_field)


                # Carrega os objetos pais a partir dos dados modificados nas entidades filhas
                lista_ids_entidades_atualizar = []
                for _chave, _campo_lista in service._dto_class.list_fields_map.items():
                    _sub_entidade = _campo_lista.entity_type.table_name
                    _sub_data_ultima_integracao = entidades_pendentes_bd.get(_sub_entidade, data_ultima_integracao)
                    _campo_id_pai = _campo_lista.related_entity_field

                    para_apagar    = _dao.listar_dados_exclusao(_campo_id_pai, _sub_entidade, _sub_data_ultima_integracao)
                    para_atualizar = _dao.listar_dados_alteracao(_campo_id_pai, _sub_entidade, _sub_data_ultima_integracao)

                    lista_ids_entidades_atualizar = list(set(lista_ids_entidades_atualizar + para_apagar + para_atualizar))


                if lista_ids_entidades_atualizar:
                    self._log("Integrando modificações de entidades agregadas.")

                    last_current_after = None
                    current_after = None
                    filtro_atualizacao = filters.copy() if filters else {}
                    _coluna_id = service._dto_class.fields_map[service._dto_class.pk_field].entity_field

                    # A cada TAMANHO_PAGINA carrega um bloco de ids para evitar problemas de tamanho de query
                    for i in range(0, len(lista_ids_entidades_atualizar), TAMANHO_PAGINA):

                        bloco_ids = lista_ids_entidades_atualizar[i:i+TAMANHO_PAGINA]
                        # carrega os objetos filhos a partir dos ids do pai, isto é sua composição
                        filtro_atualizacao[_coluna_id] = ",".join([str(id) for id in bloco_ids if id is not None])

                        while True:

                            if self._interromper_execucao:
                                self._log("Processo interrompido pelo usuário.")
                                return

                            try:

                                _data = service.list(
                                        current_after,
                                        TAMANHO_PAGINA,
                                        fields,
                                        None,
                                        filtro_atualizacao,
                                        search_query=search_query,
                                    )

                            except AfterRecordNotFoundException as e:
                                current_after = last_current_after
                                continue

                            _count = _count + len(_data)

                            if len(_data)==0:
                                break

                            # if not self._menos_log:
                            #     self._log(f"{entidade}: {_count} registro(s)")
                            _resumo[entidade] = _resumo.get(entidade, 0) + _count

                            # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                            dict_data = self._dto_to_api(fields, _data)

                            # Mandar a bagatela por apis
                            _erros_envio += self._enviar_dados(dict_data, entidade, parar_caso_erros)

                            self._processar_blobs(entidade, service, dict_data, True, parar_caso_erros)

                            # Aponta a leitura para a próxima página
                            _last = _data[-1]
                            last_current_after = current_after
                            current_after = getattr(_last, _last.pk_field)

                if  _count == 0:
                    if not self._menos_log:
                        self._log("Sem dados para atualizar, indo adiante.")
                else:
                    if not self._menos_log:
                        self._log("Entidade integrada com sucesso.")
                    self._log(f"{entidade}: {_count} registro(s).")


                self._atualiza_data_ultima_integracao(entidade, _data_integracao[entidade], _filtros_integracao_cfg)

            self._log("")
            self._log(self._color("Integração finalizada com sucesso!", 92, _is_console))

            if _erros_envio:
                self._log(self._color("Ocorreram erros que foram ignorados durante o processo, verifique:", 91, _is_console))
                self._log("")
                self._log("\n"+("-"*80)+"\n"+self._color("\n".join(str(e)+ "\n" + "-"*80 for e in _erros_envio), 91, _is_console))

            if _resumo:
                self._log("")
                self._log(self._color(f"Resumo da integração: {', '.join(f'{k}: {v}' for k, v in _resumo.items())}", 92, _is_console))

        finally:
            self._em_execucao = False


    def integrity_fields(self, dto) -> dict:
        fields = {"root": set()}

        for _field_name in sorted(dto.integrity_check_fields_map.keys()):

            if _field_name in self._ignored_fields:
                continue

            _field_obj = dto.integrity_check_fields_map[_field_name]

            if isinstance(_field_obj, DTOField):
                fields["root"].add(_field_name)
                continue

            if isinstance(_field_obj, DTOListField):
                fields["root"].add(_field_name)
                fields.setdefault(_field_name, set())

                for _related_field in sorted(_field_obj.dto_type.integrity_check_fields_map.keys()):
                    if not _related_field in self._ignored_fields:
                        fields["root"].add(f"{_field_name}.{_related_field}")
                        fields[_field_name].add(_related_field)

        return fields


    def tratar_campos_comparacao(self, dados: dict, campos_ignorados: list):

        keys_to_delete = []
        for chave, valor in dados.items():

            # Remove timezone para comparação
            if isinstance(valor, (datetime.datetime, datetime.date)):
                if valor.tzinfo is not None:
                    dados[chave] = valor.astimezone(self._tz_br).replace(microsecond=0, tzinfo=None)
                else:
                    dados[chave] = valor.replace(microsecond=0, tzinfo=None)


            if "created_by" in dados and not dados["created_by"] is None:
                if not isinstance(dados["created_by"], dict):
                    try:
                        _value_dict = json_loads(dados["created_by"])
                        dados["created_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dados["created_by"] = {"id": dados["created_by"]}

            if "updated_by" in dados and not dados["updated_by"] is None:
                if not isinstance(dados["updated_by"], dict):
                    try:
                        _value_dict = json_loads(dados["updated_by"])
                        dados["updated_by"] = _value_dict
                    except (TypeError, ValueError, JsonLoadException):
                        dados["updated_by"] = {"id": dados["updated_by"]}

            # Ignora campos não úteis
            if chave in campos_ignorados:
                keys_to_delete.append(chave)

            # Aplica regras em sublistas
            if isinstance(valor, list):
                valor.sort(key=lambda x: x['id'])
                for item in valor:
                    self.tratar_campos_comparacao(item, campos_ignorados)

        for chave in keys_to_delete:
            del dados[chave]


    def converte_dados_para_hash(self, dto, integrity_fields):

        data = dto.convert_to_dict(integrity_fields)

        self.tratar_campos_comparacao(data, self._ignored_fields)

        concatenated_values = json_dumps(data)

        data['tenant'] = self.tenant

        return {
            'id': str(data[dto.pk_field]),
            'hash': hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest(),
            '_source': data,
            '_source_hash': concatenated_values
        }

    def comparar_ids(self, dados_referencia, dados_comparacao):

        if dados_referencia['registros'] != dados_comparacao['registros']:
            self._log(self._color(f"Existem diferenças nas quantidades de dados:\r\n\r\nLocal: {dados_referencia['registros']}\r\n\r\nWeb  : {dados_comparacao['registros']}", 91, _is_console))


        # Índices para facilitar busca por ID (mantendo compatibilidade com a saída esperada do método)
        idx_referencia = {item['id']: item for item in dados_referencia['dados']}
        idx_comparacao = {item: {'id':item} for item in dados_comparacao['dados']}


        # Inicializar listas de mudanças
        _criar = []
        _excluir = []

        # Verificar itens nos dados de referência
        for item_id, item_ref in idx_referencia.items():
            if item_id not in idx_comparacao:
                # Criar se não existe nos dados de comparação
                _criar.append(item_ref['_source'])

        # Verificar itens nos dados de comparação
        for item_id in idx_comparacao.keys():
            if item_id not in idx_referencia:
                # Excluir se não existe em A
                _excluir.append(idx_comparacao[item_id]['id'])

        return _criar, _excluir


    def comparar_dados(self, dados_referencia, dados_comparacao):

        if dados_referencia['campos']['_'] != dados_comparacao['campos']['_']:
            self._log(self._color(f"Existem diferenças entre os campos comparados:\r\n\r\nLocal: {dados_referencia['campos']['_']}\r\n\r\nWeb  : {dados_comparacao['campos']['_']}", 91, _is_console ))

        if dados_referencia['registros'] != dados_comparacao['registros']:
            self._log(self._color(f"Existem diferenças nas quantidades de dados:\r\n\r\nLocal: {dados_referencia['registros']}\r\n\r\nWeb  : {dados_comparacao['registros']}", 91, _is_console))

        # Índices para facilitar busca por ID
        idx_referencia = {item['id']: item for item in dados_referencia['dados']}
        idx_comparacao = {item['id']: item for item in dados_comparacao['dados']}

        # Inicializar listas de mudanças
        _criar = []
        _atualizar = []
        _excluir = []
        _diff:List[tuple] = []

        # Verificar itens nos dados de referência
        for item_id, item_ref in idx_referencia.items():
            if item_id not in idx_comparacao:
                # Criar se não existe nos dados de comparação
                _criar.append(item_ref['_source'])
            elif item_ref['hash'] != idx_comparacao[item_id]['hash']:
                # Atualizar se o hash é diferente
                _atualizar.append(item_ref['_source'])
                # Adiciona para exibir os dados puros se disponível
                if '_source' in idx_comparacao[item_id]:
                    a = json_loads(item_ref['_source_hash'])
                    b = json_loads(idx_comparacao[item_id]['_source'])
                    _diff.append((a,b))

        # Verificar itens nos dados de comparação
        for item_id in idx_comparacao.keys():
            if item_id not in idx_referencia:
                # Excluir se não existe em A
                _excluir.append(idx_comparacao[item_id]['id'])

        return _criar, _atualizar, _excluir, _diff


    def _log_integridade(self, msg):
        _du.save_to_file(f'{self._integridade_dir}/log_diferencas_integridade.log', msg)


    def _color(self, text, code, console):
        if console:
            return f"\033[{code}m{text}\033[0m"
        else:
            return text


    def _log_comparacao_objetos(self, id, obj1, obj2, caminho='', console=False):
        _out = self._log if console else self._log_integridade

        if isinstance(obj1, dict) and isinstance(obj2, dict):
            for k in set(obj1.keys()).union(obj2.keys()):
                self._log_comparacao_objetos(id, obj1.get(k), obj2.get(k), f"{caminho}.{k}" if caminho else k)
        elif isinstance(obj1, list) and isinstance(obj2, list):
            max_len = max(len(obj1), len(obj2))
            for i in range(max_len):
                item1 = obj1[i] if i < len(obj1) else None
                item2 = obj2[i] if i < len(obj2) else None
                _id = obj1[i]['id'] if not item1 is None else obj2[i]['id'] if not item2 is None else 'indefinido'
                self._log_comparacao_objetos(id, item1, item2, f"{caminho}[{_id}]")
        else:
            s1 = str(obj1)
            s2 = str(obj2)
            if s1 != s2:
                s1_pad = s1.ljust(25)
                s2_pad = s2.ljust(25)
                _id = str(id)

                _out(f"{_id:<40} {caminho:<40} {self._color(s1_pad, '31', console)} {self._color(s2_pad, '32', console)}")


    def _log_diferencas(self, entidade, data_ultima_integracao, console=False):
        _out = self._log if console else self._log_integridade
        _out("\r\n")
        _out("-" * 130)
        _out(f"Entidade: {self._color(entidade, '36', console)}")
        _out(f"Data da última integração: {self._color(data_ultima_integracao, '36', console)}")
        _out(f"{'ID':<40} {'Campo':<40} {'Local':<25} {'Nuvem':<25}")
        _out("-" * 130)


    def _log_cabecalho(self, entidade, data_ultima_integracao, console=False):
        _out = self._log if console else self._log_integridade
        _out("\r\n")
        _out("=" * 130)
        _out(f"Entidade: {self._color(entidade, '36', console)}")
        _out(f"Data da última integração: {self._color(data_ultima_integracao, '36', console)}")


    def _log_grupo(self, titulo, detalhado=False, console=False):
        _out = self._log if console else self._log_integridade
        _out("=" * 130)
        _out(f"{titulo}:")
        _out(f"{'ID':<40} {'Campo':<40} {'Local':<25} {'Nuvem':<25}" if detalhado else "ID")
        _out("=" * 130)


    def _log_id(self, _id, console=False):
        _out = self._log if console else self._log_integridade
        _out(f"{_id}")


    @medir_tempo("Verificação de integridade")
    def executar_verificacao_integridade(
        self,
        entidades: list,
        tipo_verificacao: TipoVerificacaoIntegridade = TipoVerificacaoIntegridade.HASH,
        parar_caso_diferencas : bool = False,
        detalhar_diferencas: bool = False,
        corrigir_auto: bool = False,
        tenant: int = 0,
        trace: bool = False
    ):
        self._interromper_execucao = False
        self._em_execucao = True

        try:

            assert self._integracao_foi_configurada(), "Integração não configurada!"

            _dao = self._integracao_dao()

            assert _dao.existem_grupos_empresariais_integracao_ativos(), "Nenhum grupo empresarial ativo para integração."

            self._log(f"Executando verificação de integridade para o Tenant: {self.tenant} .")

            self._detalhar_diferencas = detalhar_diferencas

            self._trace = trace

            if corrigir_auto:
                assert self.tenant==tenant, "Tenant informado para correção não é igual ao configurado"

            self._integridade_dir = f"verificacao_integridade_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Remover entidades que nao devem ser processadas
            entidades_verificacao = copy.copy(_entidades_integracao)
            if entidades:
                for entidade in entidades:
                    assert entidade in _entidades_integracao, f"Entidade '{entidade}' não consta como entidade para integração!"

                for entidade in _entidades_integracao:
                    if not entidade in entidades:
                        entidades_verificacao.remove(entidade)


            self._log(f"{len(entidades_verificacao)} entidade(s) para verificar integridade.")

            _diferencas = False
            _idx = 0
            _resumo = defaultdict(list)
            _exclusoes_retentar = []
            _atualizacoes_retentar = []
            for entidade in entidades_verificacao:

                if  entidade in _ignorar_integridade:
                    continue

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                _idx += 1
                self._log(f"Verificando integridade {entidade}, {_idx} de {len(entidades_verificacao)}.")

                # Carregar dados paginados para integrar
                service = self._injector.service_for(entidade, True)

                _count = 0
                current_after = None
                fields = self._fields_to_load(service._dto_class)
                _filtros_particionamento = self._filtro_particionamento_de(entidade)
                _filtros_integracao_cfg = self._filtros_integracao_cfg(entidade)
                filters = (
                    _filtros_particionamento
                    | _cfg_filtros_to_dto_filtro(_filtros_integracao_cfg)
                    #| {"id":""}
                    #| {"lastupdate":"2025-05-15 00:00:00"}
                )
                search_query = None
                _integrity_fields = self.integrity_fields(service._dto_class)
                _dados_locais = []

                self._log("Extraindo dados para comparação.")
                while True:

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    if (tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR) and not corrigir_auto:

                        _dao = self._injector.integridade_dao(service._entity_class)
                        _entity_filters = service._create_entity_filters(filters)
                        _data = _dao.list_ids_integridade(
                            after=current_after,
                            limit=TAMANHO_PAGINA,
                            order_fields=None,
                            filters=_entity_filters
                        )
                    else:

                        _data = service.list(
                            current_after,
                            TAMANHO_PAGINA,
                            fields,
                            None,
                            filters,
                            search_query=search_query,
                        )

                    _count = _count + len(_data)

                    if len(_data)==0:
                        break

                    self._log(f"{_count} registro(s).")

                    # Aponta a leitura para a próxima página
                    _last = _data[-1]
                    if tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR and not corrigir_auto:
                        current_after = _last
                    else:
                        current_after = getattr(_last, _last.pk_field)

                    # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                    if tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR:

                        if corrigir_auto:
                            _data = self._dto_to_api(fields, _data)
                            while _data:
                                _item = _data.pop(0)
                                _dados_locais.append({
                                    'id': str(_item['id']),
                                    '_source': _item
                                })
                        else:
                            while _data:
                                _item = _data.pop(0)
                                _dados_locais.append({
                                    'id': str(_item),
                                    '_source': {'id' : _item }
                                })
                    else:

                        _cp_fields = copy.deepcopy(_integrity_fields)
                        while _data:
                            dto = _data.pop(0)
                            _dados_locais.append(self.converte_dados_para_hash(dto, _cp_fields))


                if tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR:
                    _campos = service._dto_class.pk_field
                else:
                    _campos = ",".join(sorted(_integrity_fields['root']))

                    #break

                _dados_locais = {
                    'registros' : _count,
                    'campos': {
                        "_": _campos,
                    },
                    'dados': _dados_locais
                }

                # captura os dados de integridade da entidade
                self._log("Consultando dados da api.")
                _dados = []
                _ultimo_id = None
                _count = 0
                while True:

                    if self._interromper_execucao:
                        self._log("Processo interrompido pelo usuário.")
                        return

                    try:
                        _dados_remotos = self._api_client.consultar_integridade_de(
                            entidade, filters, _filtros_integracao_cfg,
                            _ultimo_id, detalhar_diferencas, self.api_key, self.tenant,
                            tipo_verificacao
                        )
                    except Exception as e:
                        self._log("")
                        self._log(f"\n{'-'*80}\nErro:\n{str(e)}\n{'-'*80}")
                        self._log("")
                        raise e

                    _count = _count + len(_dados_remotos['dados'])

                    if len(_dados_remotos['dados']) == 0:
                        break

                    self._log(f"{_count} registro(s).")

                    _dados = _dados + copy.copy(_dados_remotos['dados'])

                    if tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR:
                        _ultimo_id = _dados[-1]
                    else:
                        _ultimo_id = _dados[-1]['id']

                    #break

                _dados_remotos['dados'] = _dados
                _dados_remotos['registros'] = _count

                self._log("Comparando dados.")

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                # Compara os dados e obtem o que se deve fazer
                para_criar, para_atualizar, para_apagar, _diff = [], [], [] ,[]

                if tipo_verificacao is TipoVerificacaoIntegridade.IDENTIFICADOR:
                    para_criar, para_apagar = self.comparar_ids(_dados_locais, _dados_remotos)
                else:
                    para_criar, para_atualizar, para_apagar, _diff = self.comparar_dados(_dados_locais, _dados_remotos)

                if para_criar or para_atualizar or para_apagar:
                    _resumo[entidade].append(self._color(f"Local: {_dados_locais['registros']}  Web: {_dados_remotos['registros']}", 93, _is_console))

                    _dt_ultima_integracao = self._dao_intg.data_ultima_integracao(entidade)
                    self._log_cabecalho(entidade, _dt_ultima_integracao, _is_console)

                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return

                if para_apagar:
                    _resumo[entidade].append(self._color(f"Para apagar -> {len(para_apagar)}", 93, _is_console))
                    self._log(self._color(f"\r\n{_resumo[entidade][-1]}\r\n", 93, _is_console))

                    self._log_grupo(f"Dados que serão excluídos: {len(para_apagar)}", False, _is_console)

                    if _diff:
                        for _desktop in para_apagar:
                            self._log_comparacao_objetos(_desktop, _desktop, None)
                    else:
                        for _desktop in para_apagar:
                            self._log_id(_desktop, _is_console)

                    if corrigir_auto:
                        self._log(f"\r\nRemovendo dados em {entidade}.\r\n")

                        for i in range(0, len(para_apagar), TAMANHO_PAGINA):
                            _dados_pagina = para_apagar[i:i+TAMANHO_PAGINA]

                            try:
                                mensagens = self._api_client.apagar_dados(_dados_pagina, entidade, self.api_key, self.tenant)
                                self._processa_mensagens(mensagens)
                            except Exception:
                                _exclusoes_retentar.append((entidade, _dados_pagina))


                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return


                if para_criar:
                    _resumo[entidade].append(self._color(f"Para criar -> {len(para_criar)}", 93, _is_console))
                    self._log(self._color(f"\r\n{_resumo[entidade][-1]}\r\n", 93, _is_console))

                    self._log_grupo(f"Dados que serão criados: {len(para_criar)}", False, _is_console)

                    if _diff:
                        for _desktop in para_criar:
                            self._log_comparacao_objetos(_desktop['id'], _desktop, {})
                    else:
                        for _desktop in para_criar:
                            self._log_id(_desktop['id'], _is_console)

                    if corrigir_auto:
                        self._log(f"\r\nCriando dados em {entidade}.\r\n")

                        for i in range(0, len(para_criar), TAMANHO_PAGINA):
                            _dados_pagina = para_criar[i:i+TAMANHO_PAGINA]
                            try:
                                self._api_client.enviar_dados(_dados_pagina, entidade, self.api_key)
                            except Exception:
                                _atualizacoes_retentar.append((entidade, _dados_pagina))

                            self._processar_blobs(entidade, service, _dados_pagina, False)


                if self._interromper_execucao:
                    self._log("Processo interrompido pelo usuário.")
                    return


                if para_atualizar:
                    _resumo[entidade].append(self._color(f"Para atualizar -> {len(para_atualizar)}", 93, _is_console))
                    self._log(self._color(f"\r\n{_resumo[entidade][-1]}\r\n", 93, _is_console))

                    self._log_grupo(f"Dados que serão atualizados: {len(para_atualizar)}", _diff, _is_console)

                    if _diff:
                        _i : int = 0
                        for _desktop, _web in _diff:
                            _i  += 1
                            self._log_comparacao_objetos(_desktop['id'], _desktop, _web)
                            self._trace_check(f"{self._integridade_dir}/integridade_{entidade.replace('.','_')}_{_desktop['id']}_{_i}_LOCAL.txt", json_dumps(_desktop))
                            self._trace_check(f"{self._integridade_dir}/integridade_{entidade.replace('.','_')}_{_web['id']}_{_i}_REMOTE.txt", json_dumps(_web))
                    else:
                        for _desktop in para_atualizar:
                            self._log_id(_desktop['id'], _is_console)

                    if corrigir_auto:
                        self._log(f"\r\nAtualizando dados em {entidade}.\r\n")

                        for i in range(0, len(para_atualizar), TAMANHO_PAGINA):
                            _dados_pagina = para_atualizar[i:i+TAMANHO_PAGINA]
                            try:
                                self._api_client.enviar_dados(_dados_pagina, entidade, self.api_key)
                            except Exception:
                                _atualizacoes_retentar.append((entidade, _dados_pagina))

                            self._processar_blobs(entidade, service, _dados_pagina)


                if not _diferencas:
                    _diferencas = para_criar or para_atualizar or para_apagar

                if parar_caso_diferencas and (para_criar or para_atualizar or para_apagar) and not corrigir_auto:
                    break

            # Retentando correções que falharam em ordem reversa
            _erros_envio = []
            if _atualizacoes_retentar or _exclusoes_retentar:

                self._log("Enviando ajustes de dados que falharam na primeira tentativa.")

                for _entidade_retentativa, _dados_pagina in reversed(_exclusoes_retentar):
                    self._log(f"\r\nRemovendo dados em {_entidade_retentativa}.\r\n")
                    _erros_envio += self._apagar_dados(_dados_pagina, _entidade_retentativa)

                for _entidade_retentativa, _dados_pagina in reversed(_atualizacoes_retentar):
                    self._log(f"\r\nCriando/Atualizando dados em {_entidade_retentativa}.\r\n")
                    _service = None
                    _erros_envio += self._enviar_dados(_dados_pagina, _entidade_retentativa)
                    self._processar_blobs(_entidade_retentativa, _service, _dados_pagina)


            if _diferencas:
                self._log(self._color("\r\nOcorreram diferenças na checagem da integridade, verifique a saída.\r\n", 93, _is_console))

            if not _diferencas:
                self._log(self._color("Verificação finalizada sem diferenças!\r\n", 92, _is_console))

            if _resumo:
                self._log(self._color("Resumo da integração:\r\n", 92, _is_console))
                for entidade, detalhes in _resumo.items():
                    self._log(f"{entidade}:  " + '\n'.join(detalhes) + "\n")

                if corrigir_auto:
                    self._log(self._color("Foram enviados dados de correção durante o processo, verifique a saída.\r\n",92, _is_console))

            if _erros_envio:
                self._log(self._color("Ocorreram erros que foram ignorados durante o processo, verifique:", 91, _is_console))
                self._log("")
                self._log("\n"+("-"*80)+"\n"+self._color("\n".join(str(e)+ "\n" + "-"*80 for e in _erros_envio), 91, _is_console))

        finally:
            self._em_execucao = False
