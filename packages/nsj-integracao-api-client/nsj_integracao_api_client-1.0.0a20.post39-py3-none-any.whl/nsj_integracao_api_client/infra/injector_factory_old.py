import os
import importlib
# import inspect
# import pkgutil
import sqlalchemy

from nsj_rest_lib.injector_factory_base import NsjInjectorFactoryBase
from nsj_rest_lib.dao.dao_base import DAOBase

from nsj_rest_lib.dto.dto_base import DTOBase, DTOFieldFilter
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_list_field import DTOListField
from nsj_rest_lib.descriptor.filter_operator import FilterOperator
from nsj_rest_lib.service.service_base import ServiceBase

import nsj_integracao_api_entidades.config
from nsj_integracao_api_entidades.entity_registry import EntityRegistry

nsj_integracao_api_entidades.config.tenant_is_partition_data = False
"""
 Configurando a flag para que o campo tenant não seja usado como partição localmente,
 isso inibe que o campo tenant seja usado como filtro, o que só é importante na web.
"""

from nsj_integracao_api_client.service.integrador_cfg import (
    _entidades_filtros_integracao, _filtro_nome)


db_pool = None

class InjectorFactory(NsjInjectorFactoryBase):

    # _dtos: dict = {}
    # _entities: dict = {}
    _entity_registry = EntityRegistry()

    def __enter__(self):

        if db_pool is not None:
            pool = db_pool
        else:
            assert os.getenv("bd_user") and os.getenv("bd_senha") and \
                   os.getenv("bd_host") and os.getenv("bd_porta") and \
                   os.getenv("bd_nome"), "Variáveis de conexão não informadas"

            pool = sqlalchemy.create_engine(
                sqlalchemy.engine.URL.create(
                    "postgresql+pg8000",
                    username=os.getenv("bd_user"),
                    password=os.getenv("bd_senha", None),
                    host=os.getenv("bd_host", None),
                    port=os.getenv("bd_porta", None),
                    database=os.getenv("bd_nome", None),
                ),
                poolclass=sqlalchemy.pool.NullPool,
                encoding="utf-8"
            )

        self._db_connection = pool.connect()
        self._db_connection.execute("select set_config('symmetric.triggers_disabled', '1', false);")
        #self._db_connection.execute("SET TIME ZONE 'America/Sao_Paulo';")

        return self

    def db_adapter(self):
        from nsj_gcf_utils.db_adapter2 import DBAdapter2

        return DBAdapter2(self._db_connection)

    def generic_dao(self, entity_class)-> DAOBase:
        return DAOBase(self.db_adapter(), entity_class)

    #treta de hoje - auto register
    def entity_for(self, entity_name: str):

        return self._entity_registry.entity_for_v3(entity_name)

    def dto_for(self, entity_name: str, adiciona_filtros_data: bool = False):

        _classe : DTOBase = self._entity_registry.dto_for_v3(entity_name)
        if _classe is None:
            raise KeyError(f"Não existe um DTO correpondente a tabela {entity_name}")

        # Adicionando campos de filtro de (ponto de corte) no DTO
        if _entidades_filtros_integracao[entity_name]:
            for _filtro in _entidades_filtros_integracao[entity_name]:
                _alias = _filtro_nome(_filtro)
                _operator = (
                    getattr(FilterOperator, _filtro['operador'].upper(), FilterOperator.EQUALS)
                )
                _filter = DTOFieldFilter(_alias, _operator)
                _filter.set_field_name(_filtro['campo'])
                _classe.field_filters_map[_alias] = _filter


        if adiciona_filtros_data:
            # Adicionando campos de filtro no DTO
            # _classe.field_filters_map['created_at'] = DTOFieldFilter('created_at', FilterOperator.GREATER_THAN)
            # _classe.field_filters_map['created_at'].set_field_name('created_at')
            _classe.field_filters_map['lastupdate'] = DTOFieldFilter('lastupdate', FilterOperator.GREATER_THAN)
            _classe.field_filters_map['lastupdate'].set_field_name('lastupdate')

            # if not 'created_at' in _classe.fields_map.keys():
            #     _classe.fields_map['created_at'] = DTOField()

            if not 'lastupdate' in _classe.fields_map.keys():
                _classe.fields_map['lastupdate'] = DTOField()

            # Adiciona também as entidades agregadas
            for _list_field in _classe.list_fields_map.keys():

                _sub_dto = _classe.list_fields_map[_list_field].dto_type

                _sub_dto.field_filters_map['lastupdate'] = DTOFieldFilter('lastupdate', FilterOperator.GREATER_THAN)
                _sub_dto.field_filters_map['lastupdate'].set_field_name('lastupdate')

                if not 'lastupdate' in _sub_dto.fields_map.keys():
                    _sub_dto.fields_map['lastupdate'] = DTOField()


        return _classe

    def service_for(self, entity_name: str,  adiciona_filtros_data: bool = False) -> ServiceBase:
        _entity_class = self.entity_for(entity_name)
        _dto_class = self.dto_for(entity_name, adiciona_filtros_data)
        _dto_response_class = _dto_class

        return ServiceBase(
            self,
            DAOBase(self.db_adapter(), _entity_class),
            _dto_class,
            _entity_class,
            _dto_response_class
        )

    def url_diretorio(self):
        os.getenv("bd_user")

    # Customs
    def integracao_dao(self):
        from nsj_integracao_api_client.dao.integracao import IntegracaoDAO
        return IntegracaoDAO(self.db_adapter())

    def job_dao(self):
        from nsj_integracao_api_client.dao.job import JobDAO
        return JobDAO(self.db_adapter())
