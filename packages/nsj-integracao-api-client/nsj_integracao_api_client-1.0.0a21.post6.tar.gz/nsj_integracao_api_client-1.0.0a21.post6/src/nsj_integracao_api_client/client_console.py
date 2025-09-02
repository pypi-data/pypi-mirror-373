import sys
from typing import List
import  argparse
from argparse import ArgumentError
import traceback
import datetime
import os
import sentry_sdk

from nsj_integracao_api_client.infra.injector_factory import InjectorFactory

import nsj_integracao_api_client.service.integrador as integrador
from nsj_integracao_api_client.service.integrador_cfg import (
    TipoVerificacaoIntegridade, _entidades_integracao
)

ONLY_CONSOLE = os.getenv('ONLY_CONSOLE', 'false').lower()=='true'

if not ONLY_CONSOLE:
    from nsj_integracao_api_client.app.ui.aplicacao import(
        app, render_view
    )
    from nsj_integracao_api_client.app.ui.checkable_combobox import CheckableComboBox

    from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QCheckBox, QTableWidget, QSizePolicy
    from PyQt5.QtCore import QTimer, Qt
    from PyQt5.QtGui import QTextCursor
    from PyQt5 import QtWidgets

    import nsj_integracao_api_client.app.ui.mensagem as msg_window
    import nsj_integracao_api_client.app.ui.acompanhamento as acompanhamento_window
    import nsj_integracao_api_client.app.ui.ativacao as ativacao_window
    import nsj_integracao_api_client.app.ui.conf_carga_continua as conf_carga_continua_window
    import nsj_integracao_api_client.app.ui.configurada as configurada_window
    import nsj_integracao_api_client.app.ui.configuracoes_gerais as conf_gerais_window
    import nsj_integracao_api_client.app.ui.browser_execucoes as browser_execucoes_window
    import nsj_integracao_api_client.app.ui.browser_execucoes_detail as browser_execucoes_detail_window
    import nsj_integracao_api_client.app.ui.carga_inicial as carga_inicial_window
    import nsj_integracao_api_client.app.ui.integracao as integracao_window
    import nsj_integracao_api_client.app.ui.verificacao_integridade as verificacao_integridade_window

else:
    class QApplication: pass
    class QTableWidgetItem: pass
    class QCheckBox: pass
    class QTableWidget: pass
    class QTimer: pass
    class Qt: pass
    class QTextCursor: pass
    class CheckableComboBox: pass
    class QSizePolicy: pass
    class msg_window:
        class QMessageBox: pass
        class QWidget: pass
    class acompanhamento_window:
        class Ui_FormAcompanhamento: pass
    class ativacao_window:
        class Ui_FormIntegracaoNaoConfigurada: pass
    class conf_carga_continua_window:
        class Ui_FormCargaContinua: pass
    class configurada_window:
        class Ui_FormIntegracaoConfigurada: pass
    class conf_gerais_window:
        class Ui_FormConfiguracoesGerais: pass
    class browser_execucoes_window:
        class Ui_BrowserExecucoes: pass
    class browser_execucoes_detail_window:
        class Ui_BrowserDetalhes: pass
    class carga_inicial_window:
        class Ui_FormCargaInicial: pass
    class integracao_window:
        class Ui_FormIntegracao: pass
    class verificacao_integridade_window:
        class Ui_FormVerificacaoIntegridade: pass



from time import sleep
from nsj_integracao_api_client.infra.token_service import TokenService

from nsj_gcf_utils.json_util import json_dumps
from typing import Callable

class ClientConsole:

    _modo_interativo : bool
    _modo_janela : bool
    _log_lines: List[str]
    _env: integrador.Environment
    _tenant: int
    _tenant_espelho: int
    _message_listeners: List[Callable[[str], None]]
    _error_listeners: List[Callable[[str], None]]

    #Services

    _integrador_service: integrador.IntegradorService

    #views
    _view_principal: configurada_window.Ui_FormIntegracaoConfigurada
    _view_acompanhamento: acompanhamento_window.Ui_FormAcompanhamento

    #
    _carga_params = None
    _integracao_params = None
    _integridade_params = None

    def __init__(self):
        self._modo_interativo = False
        self._modo_janela = False
        self._log_lines = []

        self._view_acompanhamento = None
        self._view_principal = None

        self._env = integrador.Environment.PROD
        self._tenant = None
        self._tenant_espelho = None
        self._message_listeners = []
        self._error_listeners = []

        self.parser = argparse.ArgumentParser(description="Cliente Console", exit_on_error=False)
        self.parser.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in integrador.Environment], type=lambda x: integrador.Environment[x.upper()], default=integrador.Environment.PROD)
        self.parser.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)
        self.parser.add_argument("-i", "--modo_interativo", help="Inicia o modo interativo", action="store_true")

        self.subparsers = self.parser.add_subparsers(dest="command")

        # Subcomando padrão
        self.parser_recarga = self.subparsers.add_parser("integrar", help="Executa a integracao de dados enfileirados")
        self.parser_recarga.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser_recarga.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_recarga.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in integrador.Environment], type=lambda x: integrador.Environment[x.upper()], default=integrador.Environment.PROD)
        self.parser_recarga.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)
        self.parser_recarga.add_argument("-v", "--verboso", help="Detalhamento do log", action="store_true")
        self.parser_recarga.add_argument("-dl", "--data_no_log", help="Se o log deve imprimir data nas entradas", action="store_true")
        self.parser_recarga.add_argument(
            "-p", "--parar_caso_erros",
            help="Parar a execução caso ocorra algum erro durante a carga inicial",
            default=False,
            action="store_true"
        )


        # Subcomando verificar integridade
        self.parser_integridade = self.subparsers.add_parser("verificar_integridade", help="Executa uma verificação de integridade, comparando os dados locais e remotos.")
        self.parser_integridade.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser_integridade.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_integridade.add_argument("-p", "--parar_caso_diferencas", help="Parar a checagem caso encontre diferenças", default=False, action="store_true")
        self.parser_integridade.add_argument("-d", "--detalhar", help="Detalhar as diferenças encontradas", default=False, action="store_true")
        self.parser_integridade.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in integrador.Environment], type=lambda x: integrador.Environment[x.upper()], default=integrador.Environment.PROD)
        self.parser_integridade.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)
        self.parser_integridade.add_argument("-v", "--verboso", help="Detalhamento do log", action="store_true")
        self.parser_integridade.add_argument("-dl", "--data_no_log", help="Se o log deve imprimir data nas entradas", action="store_true")
        self.parser_integridade.add_argument(
            "-tp",
            "--tipo",
            help=f"Tipo da verificação, podendo ser:\n {', '.join([e.value for e in TipoVerificacaoIntegridade])}",
            choices=[e for e in TipoVerificacaoIntegridade],
            type=lambda x: TipoVerificacaoIntegridade(x.upper()),
            default=TipoVerificacaoIntegridade.HASH
        )

        # Grupo de argumentos para correção
        group_corrigir = self.parser_integridade.add_argument_group("correção", "Argumentos necessários para correção")
        group_corrigir.add_argument("-c", "--corrigir", help="Efetua a correção dos problemas encontrados", default=False, action="store_true")
        group_corrigir.add_argument("--tenant", help="ID do tenant", type=int)


        # Subcomando para Instalação
        self.parser_instalar = self.subparsers.add_parser("instalar", help="Configura a integração para ser executada")
        self.parser_instalar.add_argument("chave_ativacao", help="Chave de ativação")
        self.parser_instalar.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_instalar.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_instalar.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in integrador.Environment], type=lambda x: integrador.Environment[x.upper()], default=integrador.Environment.PROD)


        # Subcomando para Carga Inicial
        self.parser_carga_inicial = self.subparsers.add_parser("carga_inicial", help="Executa a carga inicial")
        self.parser_carga_inicial.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser_carga_inicial.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_carga_inicial.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in integrador.Environment], type=lambda x: integrador.Environment[x.upper()], default=integrador.Environment.PROD)
        self.parser_carga_inicial.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)
        self.parser_carga_inicial.add_argument("-v", "--verboso", help="Detalhamento do log", action="store_true")
        self.parser_carga_inicial.add_argument("-dl", "--data_no_log", help="Se o log deve imprimir data nas entradas", action="store_true")
        self.parser_carga_inicial.add_argument(
            "-p", "--parar_caso_erros",
            help="Parar a execução caso ocorra algum erro durante a carga inicial",
            default=False,
            action="store_true"
        )


        # Subcomando para Ativação de Grupos Empresariais
        self.parser_add_grupos = self.subparsers.add_parser("ativar_grupos", help="executa a ativação de grupos empresariais na integração")
        self.parser_add_grupos.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_add_grupos.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")


        # Subcomando para Inativação de Grupos Empresariais
        self.parser_rem_grupos = self.subparsers.add_parser("desativar_grupos", help="executa a inativação de grupos empresariais na integração")
        self.parser_rem_grupos.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_rem_grupos.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")


    def add_message_listener(self, listener: Callable[[str], None]):

        if not callable(listener):
            raise TypeError("O listener deve ser uma função chamável com um único parâmetro 'mensagem: str'.")

        self._message_listeners.append(listener)


    def add_error_listener(self, listener: Callable[[str], None]):

        if not callable(listener):
            raise TypeError("O listener deve ser uma função chamável com um único parâmetro 'mensagem: str'.")

        self._error_listeners.append(listener)


    def mensagem(self, mensagem: str):

        for listener in self._message_listeners:
            listener(mensagem)


    def mensagem_erro(self, mensagem: str):

        for listener in self._error_listeners:
            listener(mensagem)


    def get_integrador(
            self,
            injector,
            env : integrador.Environment,
            forca_tenant: int = None,
            verboso: bool = False,
            data_no_log: bool = False
        ) -> integrador.IntegradorService:

        integrador.out_func = self.mensagem
        self._integrador_service = integrador.IntegradorService(injector, self, env, forca_tenant, not verboso, data_no_log)
        return self._integrador_service


    def executar_instalacao(self, chave_ativacao: str, grupos: List[str], env: integrador.Environment):
        self.mensagem("Executando processo de instalação da integração.")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).executar_instalacao(chave_ativacao, grupos)


    def ativar_grupos_empresariais(self, grupos: List[str], env: integrador.Environment):
        self.mensagem(f"Ativando grupos empresariais: {grupos if grupos else 'todos'}.")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).ativar_grupos_empresariais(grupos)


    def desativar_grupos_empresariais(self, grupos: List[str], env: integrador.Environment):
        self.mensagem(f"Desativando grupos empresariais: {grupos}")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).desativar_grupos_empresariais(grupos)


    # Métodos associados aos comandos
    def executar_integracao(
            self,
            entidades: List[str],
            env: integrador.Environment,
            forca_tenant: int = None,
            verboso: bool = False,
            data_no_log: bool = False,
            parar_caso_erros: bool = False
        ):
        with InjectorFactory() as injector:
            if entidades:
                self.mensagem(f"Executando integração para as entidades: {entidades}")
                _, tempo = self.get_integrador(injector, env, forca_tenant, verboso, data_no_log).executar_integracao(parar_caso_erros)
            else:
                self.mensagem("Executando integração para todas as entidades.")
                _, tempo = self.get_integrador(injector, env, forca_tenant, verboso, data_no_log).executar_integracao(parar_caso_erros)
            self.mensagem(tempo)

    def executar_carga_inicial(
            self,
            entidades: list,
            env: integrador.Environment,
            forca_tenant: int = None,
            verboso: bool = False,
            data_no_log: bool = False,
            parar_caso_erros: bool = False
        ):
        self.mensagem("Executando carga inicial.")
        with InjectorFactory() as injector:
            _, tempo = self.get_integrador(injector, env, forca_tenant, verboso, data_no_log).executar_carga_inicial(entidades, parar_caso_erros)
            self.mensagem(tempo)


    def executar_verificacao_integridade(self, args):
        self.mensagem("Executando verificação de integridade.")
        with InjectorFactory() as injector:
            _, tempo = self.get_integrador(
                    injector,
                    args.env,
                    args.forca_tenant,
                    args.verboso,
                    args.data_no_log
            ).executar_verificacao_integridade(
                args.entidades.split(",") if args.entidades else None,
                args.tipo,
                args.parar_caso_diferencas,
                args.detalhar,
                args.corrigir,
                args.tenant,
                args.traceback
            )
        self.mensagem(tempo)

    def registrar_entidades_integracao(self, env: integrador.Environment):
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).registrar_entidades_integracao()

    ################## Presenters e eventos de tela


    def _init_combo_entidades(self, view, parent, container):
        combo = CheckableComboBox(sorted(_entidades_integracao), parent=parent, placeholder="Selecionar entidades...", enable_search=True)
        combo.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container.addWidget(combo)
        view.comboEntidades = combo


    def _ativacao_presenter(self, view: ativacao_window.Ui_FormIntegracaoNaoConfigurada):

        _grupos = self.integracao_dao.listar_grupos_empresariais()
        self._monta_tabela_grupos_empresariais(view.tableGrupos, _grupos)

        def _ativar_integracao():
            try:
                chave_ativacao = view.editChaveAtivacao.text().strip()
                if not chave_ativacao:
                    msg_window.mostrar_aviso(view.widget, "O campo 'Chave de Ativação' não pode estar vazio.")
                    return

                if view.tableGrupos.rowCount() == 0:
                    msg_window.mostrar_aviso(view.widget, "Nenhum grupo empresarial encontrado.")
                    return

                _selecionados = []
                for row in range(view.tableGrupos.rowCount()):
                    checkbox = view.tableGrupos.cellWidget(row, 3)
                    if checkbox and checkbox.isChecked():
                        _selecionados.append({
                            "id": view.tableGrupos.item(row, 0).text(),
                            "codigo": view.tableGrupos.item(row, 1).text(),
                            "descricao": view.tableGrupos.item(row, 2).text(),
                            "ativo": view.tableGrupos.cellWidget(row, 3).isChecked()
                        })

                _grupos_ativar = [grupo["codigo"] for grupo in _selecionados]

                if not _grupos_ativar:
                    msg_window.mostrar_aviso(view.widget, "Nenhum grupo empresarial selecionado.")
                    return

                self.executar_instalacao(view.editChaveAtivacao.text(), _grupos_ativar, self._env)

                msg_window.mostrar_aviso(view.widget, "Integração ativada com sucesso.")

                view.widget.close()

                self._show_view(configurada_window.Ui_FormIntegracaoConfigurada(), self._default_presenter)

            except Exception as e:
                _msg = e.args[0] if e.args and len(e.args) > 0 else str(e)
                self.mensagem_erro(_msg)
                sentry_sdk.capture_exception(e)


        view.btnAtivar.clicked.connect(_ativar_integracao)

        view.btnCancelar.clicked.connect(view.widget.close)


    def _carga_inicial_presenter(self, view: carga_inicial_window.Ui_FormCargaInicial):

        def _execute():

            if msg_window.confirmar_acao(view.widget, "Deseja executar a carga inicial?"):

                self._carga_params = argparse.Namespace(
                    entidades = view.comboEntidades.checked_items(),
                    verboso = view.checkVerboso.isChecked(),
                    data_no_log = view.checkDataNoLog.isChecked(),
                    parar_caso_erros = view.checkPararCasoErros.isChecked()
                )

                self._log_lines.clear()
                try:
                    self._show_view_modal(acompanhamento_window.Ui_FormAcompanhamento(), self._acompanhamento_carga_inicial_presenter)
                except  Exception as e:
                    self.mensagem_erro(str(e))
                    sentry_sdk.capture_exception(e)

        view.checkVerboso.setChecked(True)
        view.checkDataNoLog.setChecked(True)
        view.checkTraceback.setVisible(False)

        self._init_combo_entidades(view, view.groupBox, view.verticalLayout_2)

        view.buttonExecutar.clicked.connect(_execute)


    def _acompanhamento_carga_inicial_presenter(self, view: acompanhamento_window.Ui_FormAcompanhamento):

        self._view_acompanhamento = view

        _previous_show = view.widget.showEvent

        def _carga_inicial():
            try:
                self.executar_carga_inicial(
                    self._carga_params.entidades,
                    self._env,
                    self._tenant_espelho,
                    self._carga_params.verboso,
                    self._carga_params.data_no_log,
                    self._carga_params.parar_caso_erros
                )
            except Exception as e:
                _msg = e.args[0] if e.args and len(e.args) > 0 else str(e)
                self.mensagem(_msg)
                self.mensagem_erro(_msg)
                sentry_sdk.capture_exception(e)

        def on_show_event(event):
            event.accept()
            _previous_show(event)
            QTimer.singleShot(0, _carga_inicial)

        _previous_close = view.widget.closeEvent

        def on_close_event(event):
            if not self._integrador_service.em_execucao():
                event.accept()
                _previous_close(event)
                return

            if msg_window.confirmar_acao(view.widget, "Ao sair o processo será abortado. Deseja encerrar ?"):
                self._integrador_service.interromper_execucao()
                sleep(0.3)
                event.accept()
                _previous_close(event)
            else:
                event.ignore()

        view.widget.showEvent = on_show_event

        view.widget.closeEvent = on_close_event


    def _integracao_presenter(self, view: integracao_window.Ui_FormIntegracao):

        def _execute():

            if msg_window.confirmar_acao(view.widget, "Deseja executar a integração?"):

                self._integracao_params = argparse.Namespace(
                    entidades = view.comboEntidades.checked_items(),
                    verboso = view.checkVerboso.isChecked(),
                    data_no_log = view.checkDataNoLog.isChecked(),
                    parar_caso_erros = view.checkPararCasoErros.isChecked()
                )

                self._log_lines.clear()
                self._show_view_modal(acompanhamento_window.Ui_FormAcompanhamento(), self._acompanhamento_integracao_presenter)

        view.checkVerboso.setChecked(True)
        view.checkDataNoLog.setChecked(True)
        view.checkTraceback.setVisible(False)

        self._init_combo_entidades(view, view.groupBox, view.verticalLayout_2)

        view.buttonExecutar.clicked.connect(_execute)


    def _acompanhamento_integracao_presenter(self, view: acompanhamento_window.Ui_FormAcompanhamento):

        self._view_acompanhamento = view

        _previous_show = view.widget.showEvent

        def _integracao():
            try:
                self.executar_integracao(
                    self._integracao_params.entidades,
                    self._env,
                    self._tenant_espelho,
                    self._integracao_params.verboso,
                    self._integracao_params.data_no_log,
                    self._integracao_params.parar_caso_erros
                )
            except Exception as e:
                _msg = e.args[0] if e.args and len(e.args) > 0 else str(e)
                self.mensagem(_msg)
                self.mensagem_erro(_msg)
                sentry_sdk.capture_exception(e)


        def on_show_event(event):
            event.accept()
            _previous_show(event)
            QTimer.singleShot(0, _integracao)

        _previous_close = view.widget.closeEvent
        def on_close_event(event):
            if not self._integrador_service.em_execucao():
                event.accept()
                _previous_close(event)
                return

            if msg_window.confirmar_acao(view.widget, "Ao sair o processo será abortado. Deseja encerrar ?"):
                self._integrador_service.interromper_execucao()
                sleep(0.3)
                event.accept()
                _previous_close(event)
            else:
                event.ignore()

        view.widget.showEvent = on_show_event

        view.widget.closeEvent = on_close_event


    def _verificacao_integridade_presenter(self, view: verificacao_integridade_window.Ui_FormVerificacaoIntegridade):

        def _execute():

            if msg_window.confirmar_acao(view.widget, "Deseja executar a verificação de integridade?"):

                self._verificacao_params = argparse.Namespace(
                    entidades = ",".join(view.comboEntidades.checked_items()),
                    tipo = integrador.TipoVerificacaoIntegridade.from_str(view.cmbTpVerificacao.currentText()),
                    parar_caso_diferencas = view.checkPararCasoDif.isChecked(),
                    detalhar = view.checkDetalharDiff.isChecked(),
                    corrigir = view.checkCorrigir.isChecked(),
                    tenant=self._tenant,
                    env=self._env,
                    forca_tenant=self._tenant_espelho,
                    traceback = view.checkTraceback.isChecked(),
                    verboso = view.checkVerboso.isChecked(),
                    data_no_log = view.checkDataNoLog.isChecked(),
                )

                self._log_lines.clear()
                self._show_view_modal(acompanhamento_window.Ui_FormAcompanhamento(), self._acompanhamento_verificacao_integridade_presenter)

        view.checkVerboso.setChecked(True)
        view.checkDataNoLog.setChecked(True)
        view.checkTraceback.setVisible(False)

        self._init_combo_entidades(view, view.groupBox, view.verticalLayout_2)

        view.cmbTpVerificacao.addItems([env.name for env in integrador.TipoVerificacaoIntegridade if env not in [integrador.TipoVerificacaoIntegridade.CONTAGEM, integrador.TipoVerificacaoIntegridade.ATRIBUTO]])
        view.cmbTpVerificacao.setCurrentText(integrador.TipoVerificacaoIntegridade.HASH.name)

        view.buttonExecutar.clicked.connect(_execute)


    def _acompanhamento_verificacao_integridade_presenter(self, view: acompanhamento_window.Ui_FormAcompanhamento):

        self._view_acompanhamento = view

        _previous_show = view.widget.showEvent

        def _integridade():
            try:
                self.executar_verificacao_integridade(self._verificacao_params)

            except Exception as e:
                _msg = e.args[0] if e.args and len(e.args) > 0 else str(e)
                self.mensagem(_msg)
                self.mensagem_erro(_msg)
                sentry_sdk.capture_exception(e)


        def on_show_event(event):
            event.accept()
            _previous_show(event)
            QTimer.singleShot(0, _integridade)


        _previous_close = view.widget.closeEvent
        def on_close_event(event):
            if not self._integrador_service.em_execucao():
                event.accept()
                _previous_close(event)
                return

            if msg_window.confirmar_acao(view.widget, "Ao sair o processo será abortado. Deseja encerrar ?"):
                self._integrador_service.interromper_execucao()
                sleep(0.3)
                event.accept()
                _previous_close(event)
            else:
                event.ignore()

        view.widget.showEvent = on_show_event

        view.widget.closeEvent = on_close_event


    def _agendar_carga_continua_presenter(self, view: conf_carga_continua_window.Ui_FormCargaContinua):

        def _parametros_entrada_agendamento():
            return f"-ft={self._tenant_espelho}" if self._tenant_espelho else ""


        _job_dao = self._injector.job_dao()

        _agendamento =_job_dao.get_agendamento_integracao()
        if _agendamento:
            _status = 'Agendado' if _agendamento["status"]!=3 else 'Cancelado'
            _pode_cancelar = True if _agendamento["status"]!=3 else False
            _entrada = _agendamento["entrada"] or {}

            view.labelStatus.setText(f"Status atual: {_status}")
            view.btnCancelar.setVisible(_pode_cancelar)
            view.spinIntervalo.setValue(_agendamento["intervalo"])

            view.labelParametrosValor.setText(_parametros_entrada_agendamento() if not _pode_cancelar else _entrada.get("integrar", "(Nenhum)"))

            view.btnAgendar.setText("📅 Reativar" if not _pode_cancelar else "📅 Atualizar")

        else:
            view.labelStatus.setText("Status atual: Não agendado")
            view.labelParametrosValor.setText("(Nenhum)")
            view.btnCancelar.setVisible(False)
            view.btnAgendar.setText("📅 Agendar")
            view.spinIntervalo.setValue(10)


        def agendar_job():
            try:
                _entrada = {"integrar": _parametros_entrada_agendamento()}
                _intervalo = view.spinIntervalo.value()

                _job_type = _job_dao.get_job_type_by_code('INTEGRACAO_APIS')
                if _job_type is None:
                    _job_dao.cria_job_type(0, 0, 'INTEGRACAO_APIS')

                if _agendamento:
                    _job_dao.atualiza_job(_agendamento["id"], json_dumps(_entrada), _intervalo)
                else:
                    _job_dao.agenda_job(json_dumps(_entrada), _intervalo)
                    view.labelStatus.setText("Status atual: Agendado")
                    view.labelParametrosValor.setText(_entrada["integrar"] or "(Nenhum)")
                    view.btnCancelar.setVisible(True)
                msg_window.mostrar_info(view.widget, "Agendamento realizado com sucesso")
                view.widget.close()
            except Exception as e:
                self.mensagem_erro(str(e))
                sentry_sdk.capture_exception(e)

        view.btnAgendar.clicked.connect(agendar_job)

        def cancelar_job():
            if msg_window.confirmar_acao(view.widget, "Deseja cancelar o agendamento?"):
                try:
                    _job_dao.cancela_agendamento(_agendamento["id"])
                    view.labelStatus.setText("Status atual: Não agendado")
                    view.btnCancelar.setVisible(False)
                    view.widget.close()
                except Exception as e:
                    self.mensagem_erro(str(e))
                    sentry_sdk.capture_exception(e)

        view.btnCancelar.clicked.connect(cancelar_job)


    def _conf_gerais_presenter(self, view: conf_gerais_window.Ui_FormConfiguracoesGerais):

        def checkbox_changed():
            view.lineEdit.clear()
            view.lineEdit.setEnabled(view.checkBox.isChecked())

        def salvar_cfg():
            if msg_window.confirmar_acao(view.widget):
                self._env = integrador.Environment[view.comboBox.currentText()]
                try:
                    self._tenant_espelho = int(view.lineEdit.text())
                except ValueError:
                    self._tenant_espelho = None

                self._atualiza_tela_principal()

                view.widget.close()


        def cancelar_cfg():
            view.widget.close()


        view.comboBox.addItems([env.name for env in integrador.Environment])
        view.comboBox.setCurrentText(self._env.name)


        if self._tenant_espelho:
            view.checkBox.setChecked(True)
            view.lineEdit.setText(str(self._tenant_espelho))
        else:
            view.lineEdit.setText('')
            view.lineEdit.setEnabled(False)

        view.lineEdit.setText(str(self._tenant_espelho) if self._tenant_espelho else '')

        view.checkBox.clicked.connect(checkbox_changed)

        view.btnSalvar.clicked.connect(salvar_cfg)

        view.btnCancelar.clicked.connect(cancelar_cfg)


    def _browser_execucoes_presenter(self, view: browser_execucoes_window.Ui_BrowserExecucoes):

        def _detalhes_log_presenter(view: browser_execucoes_detail_window.Ui_BrowserDetalhes, logs):
            view.plainTextEdit.clear()
            for _log in logs:
                _data = _log['datahora']
                _msg = _log['mensagem']['mensagem'] if 'mensagem' in _log['mensagem'] else _log['mensagem']
                view.plainTextEdit.appendPlainText(f'{_data} - {_msg}')


        def _on_double_click(row, _column):
            try:
                # Obter os dados da linha clicada
                job_id = view.tableDados.item(row, 1).text()

                _logs = self.integracao_dao.listar_logs_execucoes(job_id)
                form = browser_execucoes_detail_window.Ui_BrowserDetalhes()

                # Abrir a janela de detalhes da execução
                self._show_view_modal(form, lambda view: _detalhes_log_presenter(view, _logs))
            except Exception as e:
                self.mensagem_erro(str(e))
                sentry_sdk.capture_exception(e)
                #msg_window.mostrar_erro(view.widget, str(e))

        _dados = self.integracao_dao.listar_execucoes()

        view.tableDados.setSelectionBehavior(QTableWidget.SelectRows)
        view.tableDados.setEditTriggers(QTableWidget.NoEditTriggers)

        view.tableDados.setColumnHidden(0, True)
        view.tableDados.setColumnHidden(1, True)
        view.tableDados.setColumnHidden(2, True)
        view.tableDados.setColumnHidden(3, True)

        view.tableDados.setRowCount(len(_dados))
        for i, _execucao in enumerate(_dados):
            for col, key in enumerate([
                'jobtype', 'job', 'codigo', 'descricao', 'entrada', 'saida',
                'status', 'progresso', 'enfileiramento', 'inicioexecucao',
                'fimexecucao', 'duracao'
            ]):
                value = None
                if key == 'status':

                    match _execucao[key]:
                        case 0:
                            value = "Pendente"
                        case 1:
                            value = "Processando"
                        case 2:
                            value = "Concluído com sucesso"
                        case 3:
                            value = "Erro: (abortado por falta de resposta do JobManager)"
                        case 4:
                            value = "Erro: (parâmetros de entrada incorretos)"
                        case 5:
                            value = "Erro: (falha de execução)"
                        case _:
                            value = "Desconhecido"

                elif isinstance(_execucao.get(key), datetime.datetime):
                    value = str(_execucao[key].replace(microsecond=0))
                else:
                    value = str(_execucao[key]) if _execucao.get(key) is not None else ""


                view.tableDados.setItem(i, col, QTableWidgetItem(value))

        view.tableDados.resizeColumnsToContents()
        view.tableDados.cellDoubleClicked.connect(_on_double_click)


    def _monta_tabela_grupos_empresariais(self, tabela: QTableWidget, grupos: list, on_checkbox_clicked = None):

        tabela.setRowCount(len(grupos))
        # Tornar a coluna "id" invisível
        tabela.setColumnHidden(0, True)
        tabela.setColumnWidth(1, 150)
        tabela.setColumnWidth(2, 300)
        header = tabela.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)  # Coluna 1 (segunda) fica com tamanho fixo


        for i, _grupo in enumerate(grupos):
            tabela.setItem(i, 0, QTableWidgetItem(str(_grupo['id'])))
            tabela.setItem(i, 1, QTableWidgetItem(_grupo['codigo']))
            tabela.setItem(i, 2, QTableWidgetItem(_grupo['descricao']))
            _ativo = True
            if 'ativo' in _grupo:
                _ativo = _grupo['ativo']
            tabela.setItem(i, 3, QTableWidgetItem(_ativo))

            # Tornar as colunas "codigo" e "descricao" somente leitura
            tabela.item(i, 1).setFlags(tabela.item(i, 1).flags() & ~Qt.ItemIsEditable)
            tabela.item(i, 2).setFlags(tabela.item(i, 2).flags() & ~Qt.ItemIsEditable)

            # Checkbox na coluna "ativo"
            checkbox = QCheckBox()
            checkbox.setChecked(_ativo)
            checkbox.setStyleSheet("margin-left:50%; margin-right:50%;")  # Centralizar o checkbox
            tabela.setCellWidget(i, 3, checkbox)

            if on_checkbox_clicked:
                checkbox.clicked.connect(lambda state, row=i: on_checkbox_clicked(row, state))


    def _atualiza_tela_principal(self):
        self._view_principal.labelTenantDesc.setText(str(self._tenant))
        self._view_principal.labelTenantDesc.setStyleSheet("font-weight:600; color:#3d3846;")
        self._view_principal.labelAmbienteDesc.setText(self._env.name.capitalize())
        self._view_principal.labelAmbienteDesc.setStyleSheet("font-weight:600; color:#1a5fb4;")


    def _default_presenter(self, view: configurada_window.Ui_FormIntegracaoConfigurada):
        self._view_principal = view

        _tenant = 'Integração não configurada'

        _integracao_configurada = self.integracao_dao.integracao_configurada()
        if _integracao_configurada:
            _token = self.integracao_dao.recuperar_token()
            _decoded_token = TokenService().decode_token(_token)
            self._tenant = _decoded_token['tenant_id']

        self._atualiza_tela_principal()

        grupos = self.integracao_dao.listar_grupos_empresariais_integracao()

        def _on_checkbox_clicked(row, state):
            checkbox = view.tableGrupos.cellWidget(row, 3)
            if not msg_window.confirmar_acao(view.widget, "Confirma?"):
                # Reverter o estado do checkbox para o valor anterior
                checkbox.blockSignals(True)  # Bloquear sinais para evitar loops
                checkbox.setChecked(not state)
                checkbox.blockSignals(False)  # Desbloquear sinais
            else:
                try:
                    self.integracao_dao.registrar_grupos_empresariais([grupos[row]['id']])
                except Exception as e:
                    self.mensagem_erro(str(e))
                    sentry_sdk.capture_exception(e)

        self._monta_tabela_grupos_empresariais(view.tableGrupos, grupos, _on_checkbox_clicked)

        view.btnCargaInicial.clicked.connect(self._do_carga_inicial)

        view.btnIntegracao.clicked.connect(self._do_integracao)

        view.btnVerificarIntegridade.clicked.connect(self._do_verificao_integridade)

        view.btnAgendarIntegracao.clicked.connect(self._do_agendar_carga_continua)

        view.btnHistoricoIntegracoes.clicked.connect(self._do_historico_integracoes)

        view.btnAlterarConfiguracao.clicked.connect(self._do_configuracoes_gerais)

        view.btnDesativar.clicked.connect(self._do_desativar_integracao)


    def _do_carga_inicial(self):
        self._show_view_modal(carga_inicial_window.Ui_FormCargaInicial(), self._carga_inicial_presenter)


    def _do_integracao(self):
        self._show_view_modal(integracao_window.Ui_FormIntegracao(), self._integracao_presenter)


    def _do_verificao_integridade(self):
        self._show_view_modal(verificacao_integridade_window.Ui_FormVerificacaoIntegridade(), self._verificacao_integridade_presenter)


    def _do_agendar_carga_continua(self):
        self._show_view_modal(conf_carga_continua_window.Ui_FormCargaContinua(), self._agendar_carga_continua_presenter)


    def _do_configuracoes_gerais(self):
        self._show_view_modal(conf_gerais_window.Ui_FormConfiguracoesGerais(), self._conf_gerais_presenter)


    def _do_historico_integracoes(self):
        self._show_view_modal(browser_execucoes_window.Ui_BrowserExecucoes(), self._browser_execucoes_presenter)


    def _do_desativar_integracao(self):
        if msg_window.confirmar_acao(self._view_principal.widget, "Deseja desativar a integração?"):
            try:
                _existe_instalacao_symmerics = self.integracao_dao.symmetrics_instalado()

                self.integracao_dao.begin()

                if _existe_instalacao_symmerics:
                # José pediu para não ativar automático
                #    self.integracao_dao.habilitar_symmetrics_local()
                #    self.integracao_dao.habilitar_nodes_symmetrics()
                    pass
                else:
                    self.integracao_dao.remove_token_tenant()

                self.integracao_dao.commit()

                self._view_principal.widget.close()

            except Exception as e:
                self.integracao_dao.rollback()
                self.mensagem_erro(str(e))
                sentry_sdk.capture_exception(e)


    def _centralizar_janela(self,janela):
        frameGm = janela.frameGeometry()
        centro_tela = janela.screen().availableGeometry().center()
        frameGm.moveCenter(centro_tela)
        janela.move(frameGm.topLeft())


    def _show_view(self, view, presenter):
        _widget = render_view(view)
        if presenter:
            presenter(view)
        _widget.show()
        self._centralizar_janela(_widget)


    def _show_view_modal(self, view, presenter):
        _widget = render_view(view)
        if presenter:
            presenter(view)
        return _widget.exec_()


    ##############################  Modo interativo

    def _imprime_texto_tela_acompanhamento(self, mensagem: str):
        if self._modo_janela and self._view_acompanhamento:
            if 'registros...' in mensagem:
                lines = self._view_acompanhamento.plainTextEdit.toPlainText().splitlines()
                if lines and lines[-1].strip().endswith('registros...'):
                    lines[-1] = mensagem
                    self._view_acompanhamento.plainTextEdit.setPlainText("\n".join(lines))
                    self._view_acompanhamento.plainTextEdit.moveCursor(QTextCursor.End)

                else:
                    self._view_acompanhamento.plainTextEdit.appendPlainText(mensagem)
            else:
                self._view_acompanhamento.plainTextEdit.appendPlainText(mensagem)



            QApplication.processEvents()


    def _mostra_janela_erro(self, mensagem: str):
        msg_window.mostrar_erro(None, mensagem)


    def modo_janela(self):

        if ONLY_CONSOLE:
            raise Exception("Modo janela desabilitado.")

        self._modo_janela = True
        self.mensagem("Iniciando Modo janela.")
        try:
            with InjectorFactory() as injector:
                self._injector = injector
                self.integracao_dao = injector.integracao_dao()

                env_cfg = self.integracao_dao.recuperar_configuracao_ambiente()
                self._env = integrador.Environment(env_cfg) if env_cfg else self._env

                self.add_message_listener(self._imprime_texto_tela_acompanhamento)
                self.add_error_listener(self._mostra_janela_erro)

                _integracao_configurada = self.integracao_dao.integracao_configurada()
                _symmetrics_instalado = False
                _symmetrics_local_ativo = self.integracao_dao.symmetrics_local_ativo()
                _existem_nodes_symmetrics_ativos = False

                if _integracao_configurada:

                    if (_symmetrics_instalado and _existem_nodes_symmetrics_ativos) or _symmetrics_local_ativo:
                        if msg_window.confirmar_acao(None, "É necessário desabilitar a Sincronia para executar a Integração. Deseja continuar?"):
                            try:
                                self.integracao_dao.begin()

                                if _symmetrics_local_ativo:
                                    self.integracao_dao.desabilitar_symmetrics_local()

                                self.ativar_grupos_empresariais(None, self._env)
                                self.registrar_entidades_integracao(self._env)

                                self.integracao_dao.commit()
                            except Exception as e:
                                self.integracao_dao.rollback()
                                self.mensagem_erro(str(e))
                                sentry_sdk.capture_exception(e)

                        else:
                            return

                    # Se não tiver entidade configuradas para integração cria a configuração
                    if not self.integracao_dao.listar_entidades_pendentes_integracao():
                        self.registrar_entidades_integracao(self._env)


                    self._show_view(configurada_window.Ui_FormIntegracaoConfigurada(), self._default_presenter)
                else:
                    self._show_view(ativacao_window.Ui_FormIntegracaoNaoConfigurada(), self._ativacao_presenter)

                app.exec_()
        except Exception as e:
            self.mensagem_erro(str(e))
            sentry_sdk.capture_exception(e)


    def modo_interativo(self):

        def _print_erro(mensagem: str):
            print(f"\033[91m{mensagem}\033[0m")


        if len(self._message_listeners) == 0:
            self.add_message_listener(print)
            self.add_error_listener(_print_erro)

        self._modo_interativo = True
        self.mensagem("Modo interativo. Digite 'sair' para encerrar.")
        while True:
            try:
                entrada = input(">> ").strip()
                if entrada.lower() == 'sair':
                    self.mensagem("Encerrando modo interativo.")
                    break
                if entrada:
                    args = self.parser.parse_args(entrada.split())
                    self.executar_comando(args)
            except SystemExit:
                continue
            except ArgumentError as e:
                self.mensagem_erro(f"Erro: {e}")
                sentry_sdk.capture_exception(e)
            except Exception as e:
                self.mensagem_erro(f"Erro: {e}")
                if '-t' in entrada.split():
                    traceback.print_exc()
                sentry_sdk.capture_exception(e)


    def executar_comando(self, args):
        if args.command == "integrar" or args.command is None:
            self.executar_integracao(
                entidades=args.entidades.split(",") if args.entidades else None,
                env=args.env,
                forca_tenant=args.forca_tenant,
                verboso=args.verboso,
                data_no_log=args.data_no_log,
                parar_caso_erros=args.parar_caso_erros
            )
        elif args.command == "instalar":
            self.executar_instalacao(args.chave_ativacao, args.grupos.split(",") if args.grupos else [], env=args.env)
        elif args.command == "ativar_grupos":
            self.ativar_grupos_empresariais(args.grupos.split(",") if args.grupos else None, env=args.env)
        elif args.command == "desativar_grupos":
            self.desativar_grupos_empresariais(args.grupos.split(",") if args.grupos else None, env=args.env)
        elif args.command == "carga_inicial":
            self.executar_carga_inicial(
                entidades=args.entidades.split(",") if args.entidades else None,
                env=args.env,
                forca_tenant=args.forca_tenant,
                verboso=args.verboso,
                data_no_log=args.data_no_log,
                parar_caso_erros=args.parar_caso_erros
            )
        elif args.command == "verificar_integridade":
            if args.corrigir and not args.tenant:
                self.parser_integridade.error("tenant é obrigatório quando --corrigir é especificado")
            self.executar_verificacao_integridade(args)
        else:
            self.mensagem(f'Comando desconhecido: "{args.command}"')
            self.parser.print_help()


    # Configuração do parser de argumentos
    def main(self, args):

        self._env = args.env

        def _conditional_filter(event, _hint):

            if self._env == integrador.Environment.LOCAL:
                return None  # bloqueia o envio
            else:
                return event

        sentry_sdk.utils.MAX_STRING_LENGTH = 2048
        sentry_sdk.init(
            dsn="https://f35985d919a74482949f2d06c29b94dc@sentry.nasajon.com.br/80",
            environment=self._env.value,
            before_send=_conditional_filter,
            traces_sample_rate=1.0
        )

        try:
            #obter tenant configurado
            with InjectorFactory() as injector:
                _integracao_dao = injector.integracao_dao()
                _integracao_configurada = _integracao_dao.integracao_configurada()
                if _integracao_configurada:
                    _token = _integracao_dao.recuperar_token()
                    _decoded_token = TokenService().decode_token(_token)
                    self._tenant = _decoded_token['tenant_id']

                    sentry_sdk.set_tag("tenant", self._tenant_espelho if self._tenant_espelho else self._tenant)
                    sentry_sdk.set_extra("tenant", self._tenant_espelho if self._tenant_espelho else self._tenant)


            if args.modo_interativo:
                return self.modo_interativo()

            if not args.command:
                return self.modo_janela()

            if len(self._message_listeners) == 0:
                self.add_message_listener(print)
                self.add_error_listener(lambda msg: print(f"\033[91m{msg}\033[0m"))

            return self.executar_comando(args)

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e


def run():
    client = ClientConsole()
    try:
        args = client.parser.parse_args()
        client.main(args)
    except ArgumentError as e:
        client.mensagem_erro(f"Erro: Argumentos inválidos: {sys.argv}")
        sentry_sdk.capture_exception(e)
        exit(1)
    except Exception as e:
        client.mensagem_erro(f"Erro: {e}")
        sentry_sdk.capture_exception(e)
        if '-t' in sys.argv:
            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    run()
