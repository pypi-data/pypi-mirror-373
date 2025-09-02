from typing import List

from enum import Enum

import time

# Todas as entidade que fazem parte da integração
entidades_integracao: List[str] = [
    'ns.gruposempresariais',
    'ns.empresas',
    'ns.estabelecimentos',
    'pedidos.configuracoes_aprovacoes',
    'pedidos.empresas_concorrentes',
    'pedidos.potenciais_portfolios',
    'estoque.mva',
    'estoque.tabelasdeprecoscategorias',
    'estoque.tabelasdeprecosfamilias',
    #'ns.contaspadroes', nao sincronizara
    #'ns.ipienquadramentos', nao sincronizara
    'pedidos.pessoas_empresasconcorrentes',
    #'ns.locaisdeuso', nao sincronizara
    'pedidos.produtos_faixas_comissoes',
    'estoque.rotas_pessoas',
    'estoque.regrasdepagamento',
    'estoque.produtosconvunidades',
    'pedidos.produtos_faixas_precos_segmentos',
    'persona.condicoesambientestrabalho',
    'pedidos.equipes',
    'pedidos.pessoas_produtos_consumidos',
    'pedidos.equipes_vendedores',
    'ns.pessoasparcelamentos',
    'pedidos.produtos_faixas_precos_vigencias',
    'pedidos.produtos_faixas_precos',
    'persona.membroscipa',
    'estoque.classificacoesfragilidade',
#    'persona.beneficiostrabalhadoressuspensoesadesoes', Não existe local
#    'persona.beneficiostrabalhadoresadesoes', Não existe local
    'ns.conjuntosfichas',
    'persona.ambientes',
    #'ns.configuracaoacessoapi', nao sincronizara
    'ns.pessoasformaspagamentos',
    #'ns.rateios', nao sincronizara
    #'servicos.ordensservicosvisitas', nao sincronizara
    'persona.gestorestrabalhadores',
    'persona.itensfaixas',
    'persona.outrosrecebimentostrabalhadores',
    'persona.processosrubricas',
    'persona.reajustessindicatos',
    'persona.reajustestrabalhadores',
    'persona.tarifasconcessionariasvts',
    'persona.tarifasconcessionariasvtstrabalhadores',
    'persona.tiposanexos',
    'ponto.compensacoeslancamentos',
    'ponto.pagamentoslancamentos',
    #'servicos.tiposobjetosservicos', não sincroniza mais
    'servicos.tiposprojetos',
    'workflow.escopo',
    'workflow.processos',
    'persona.historicosadiantamentosavulsos',
    'pedidos.tipos_objecoes',
    'persona.convocacoestrabalhadores',
    'persona.configuracoesordemcalculomovimentos',
    'persona.dispensavalestransportestrabalhadores',
    'persona.processossuspensoes',
    'ponto.atrasosentradascompensaveistrabalhadores',
    #'estoque.custosintermediarios', não faz mais parte da sinc
    'ns.conjuntosservicos',
    #'ns.tipi', nao sincronizara
    #'ns.tiposfollowups', nao sincronizara
    #'ns.valoresclassificadoreslista', não sincroniza mais
    'ponto.pendenciascalculostrabalhadores',
    'pedidos.clientesvendedores',
    #'estoque.locaisdeestoquesenderecos', não faz mais parte
    #'ns.utilizacaonumeracaodnf',
    'persona.funcoes',
    'persona.medicos',
    'persona.rubricasponto',
    #'pcp.custos', nao sincroniza
    #'crm.itensprocessarcontaspagar', nao sincroniza
    'persona.configuracoesordemcalculomovimentosponto',
    'estoque.itens',
    'ns.conjuntosfornecedores',
    #'crm.objetosservicoshistoricoscomponentes', nao sincronizara
    #'crm.objetosservicoshistoricosofertas', nao sincronizara
    'estoque.locaisdeestoques',
    'persona.historicos',
    'estoque.rotas',
    'ns.contatos',
    'financas.titulos',
    'estoque.locaisdeestoquesoperacoes',
    #'estoque.ra', nao sincronizara
    'estoque.unidades',
    'financas.contratos',
    'financas.itenscontratos',
    'ns.df_servicos',
    # 'ns.numeros_docfis', nao sincronizara
    #'ns.obras', nao sincronizara
    #'ns.perfisusuario', nao sincronizara
    'ponto.saidasantecipadascompensaveistrabalhadores',
    'ns.estabelecimentosconjuntos',
    #'ns.gruposdeusuariosacessos', nao sincronizara
    'ns.telefones',
#    'servicos.servicoscatalogo',
    'persona.tiposhistoricos',
    'ns.conjuntosunidades',
    'ns.conjuntosvendedores',
    'financas.contas',
    'financas.layoutscobrancas',
    #'crm.assuntos', não sincroniza mais'
    #'financas.configuracoesbancarias', nao sincroizara
    'financas.contratosclientespartilhas',
    #'financas.tiposcontas', nao sincronizara
    'ns.anexosmodulos',
    #'ns.classificadores', nao sincronizara
    #'ns.classificados', nao sincronizara
    #'servicos.servicoscfops', nao sincronizara
    'persona.eventos',
    'persona.dependentestrabalhadores',
    'financas.bancos',
    'persona.beneficios',
    'persona.concessionariasvts',
    'persona.emprestimostrabalhadores',
    'persona.faixas',
    'estoque.produtos',
    'ns.cfop',
    'estoque.romaneios',
    'estoque.romaneios_notas',
    'estoque.romaneios_notas_itens',
    'compras.associacoesitensnotas',
    #'crm.parcelamentos', nao sincronizara
    'estoque.categoriasdeprodutos',
    'estoque.familias',
    'estoque.operacoes',
    'estoque.tabelasdeprecos',
    'estoque.tabelasdeprecosentidades',
    'estoque.tabelasdeprecositens',
    'estoque.tabelasdeprecosuf',
    'estoque.tabelasdeprecosestabelecimentos',
    #'estoque.proprietarios', nao sincronizara
    'estoque.motoristas',
    #'estoque.romaneios_ajudantes',
    'persona.compromissostrabalhadores',
    'pedidos.configuracoes',
    'pedidos.formasdepagamentosativas',
    'pedidos.locaisdeestoquevendedores',
    'pedidos.operacoesestabelecimentos',
    'pedidos.parcelamentosativos',
    'pedidos.produtosvendedores',
    'pedidos.tabelasdeprecosvendedores',
    'scritta.tabicms',
    'ns.conjuntos',
    'ns.conjuntosclientes',
    'ns.df_enderecos_retiradasentregas',
    'ns.contatosemails',
    'ns.df_fretes',
    'ns.df_fretes_volumes',
    'ns.df_linhas_impostos',
    'ns.df_pagamentos',
    'ns.df_parcelas',
    'ns.df_vendedores',
    'ns.df_linhas',
    'ns.formaspagamentos',
    #'ns.usuarios', nao sincronizara
    #'ns.documentositens', nao sincornizara
    'servicos.servicos',
    'financas.centroscustos',
    #'servicos.ordensservicos', nao sincronizara
    #'financas.classificacoesfinanceiras', nao sincronizara
    #'financas.rateiosfinanceiros', nao sincronizara
    'persona.avisospreviostrabalhadores',
    'compras.negociacoesitens',
    'persona.tiposdocumentoscolaboradores',
    #'servicos.fila_processamento_boletins_medicao_web', nao sincronizara
    'compras.negociacoesvalores',
    #'crm.parcelas', sincronizara
    #'servicos.tiposmanutencoes', nao sincronizara
    #'servicos.servicostecnicos', nao sincronizara
    'compras.requisicoescompras',
    'compras.solicitacoesprodutosservicos',
    #'servicos.orcamentosvariaveis',
    'persona.admissoespreliminares',
    'persona.avisosferiastrabalhadores',
    'persona.cargos',
    #'compras.itenscompras',
    #'servicos.categoriasdeservicos',
    #'servicos.orcamentoscustosmaodeobra',
    #'financas.agencias',
    #'ns.documentosged', nao sincronizara
    #'estoque.ra_historicos', nao sincronizara
    'estoque.veiculos',
    'ns.conjuntosprodutos',
    #'servicos.tiposcustosmaodeobra',
    #'servicos.orcamentosfuncoes',
    #'servicos.tiposfuncoesdetalhes', não sinc
    #'servicos.tiposservicos', nao sincronizara
    'ponto.regras',
    #'servicos.orcamentosreceitasdespesas',
    'persona.tiposfuncionarios',
    'persona.processos',
    'persona.niveiscargos',
    'persona.mudancastrabalhadores',
    'financas.contasfornecedores',
    'persona.jornadas',
    'ponto.diascompensacoestrabalhadores',
    #'servicos.operacoesordensservicos', nao sincronizara
    'persona.lotacoes',
    #'ns.classificacoes', nao sincronizara
    'estoque.saldoslocaisdeestoques',
    #'pcp.custosvalores', não sincroniza
    #'estoque.ra_itens', nao sincronizara
    'ns.enderecos',
    'servicos.objetosservicos',
    #'servicos.tiposordensservicos', nao sincronizara
    'persona.trabalhadores',
    #'servicos.ordensservicositens', nao sincronizara
    'persona.documentoscolaboradores',
    'persona.escalasfolgastrabalhadores',
    'persona.faltastrabalhadores',
    'persona.horarios',
    'persona.instituicoes',
    'persona.intervalosjornadas',
    'ns.configuracoes',
    'ns.df_docfis',
    'compras.propostascotacoes',
    #'servicos.tiposfuncoes', não sinc
    #'servicos.funcoes', nao sinc
    #'servicos.custosmaodeobra', nao sinc
    #'servicos.receitasdespesas', nao sinc
    #'servicos.variaveisorcamentarias',
    'persona.pendenciaspagamentos',
    #'crm.midiasorigem', nao sincronizara
    #'crm.negociosoperacoes', nao sincronizara
    'estoque.entregadores',
    'estoque.perfiltrib_est',
    'estoque.perfiltrib_fed',
    'estoque.figurastributarias',
    'compras.requisicoesfornecedores',
    'persona.horariosalternativostrabalhadores',
    'persona.outrosrendimentostrabalhadores',
    'persona.afastamentostrabalhadores',
    #'ns.feriados', nao sincronizara
    'persona.adiantamentosavulsos',
    'ns.pessoas',
    'compras.negociacoes',
    #'servicos.categoriasfuncoes', nao sinc
    #'servicos.atendimentos',
    'persona.departamentos',
    #'crm.promocoesleads', sincronizara
    #'crm.segmentosatuacao', nao sincronizara
    #'estoque.ra_movimentos', nao sincronizara
    'ns.pessoasmunicipios',
    'persona.horariosespeciais',
    'persona.sindicatos',
    'workflow.diagramas',
    'workflow.papeis',
    'workflow.equipes',
    'workflow.estados',
    'workflow.acoes',
    'workflow.equipesusuarios',
    'workflow.papeisequipes',
    #'crm.contratostecnicositens', NÃO FAZ MAIS PARTE SYNC
    'compras.negociacoesfornecedores',
    #'ns.followups', nao sincronizara
    'estoque.figurastributariastemplates',
    'estoque.perfiltrib_est_validades',
    #'estoque.acordosfornecimentoprodutos',não faz mais parte sync
    #'servicos.orcamentositensfaturamento', não faz mais parte sync
    #'servicos.orcamentos', não faz mais parte da sync
    #'crm.contratostecnicos', NÃO FAZ MAIS PARTE SYNC
    'persona.movimentosponto',
    'persona.beneficiostrabalhadores',
    #'crm.proximoscontatos', nao sincronizara
    'estoque.romaneios_entregas',
    'estoque.perfiltrib_fed_validades',
    'estoque.perfiltrib_fed_validades_impostos',
    'estoque.romaneios_entregadores',
#    'persona.apontamentos',
#    'servicos.componentes',
    'estoque.perfiltrib_est_validades_impostos',
    #'persona.acordosmp9362020trabalhadores',
    'persona.movimentos',
    'financas.projetos',
    #'servicos.orcamentoscustosmateriais',
    #'estoque.produtosnumerosdeserie',
    #'estoque.acordosfornecimentoprodutositens' não faz mais parte da sinc
]

_entidades_particionadas_por_grupo = [
    #'ns.gruposempresariais','ns.empresas', 'ns.configuracoes'
    'ns.gruposempresariais',
    'ns.configuracoes',
    'pedidos.clientesvendedores',
    'ns.empresas',
    'pedidos.locaisdeestoquevendedores',
    'pedidos.tabelasdeprecosvendedores',
    'pedidos.produtosvendedores',
    'financas.projetos',
    'compras.itenscompras',
    'estoque.ra_movimentos',
    'estoque.rotas',
    'financas.centroscustos',
    'financas.classificacoesfinanceiras',
    'ns.formaspagamentos',
    'ns.gruposempresariais',
    'ns.pessoasmunicipios',
    'pedidos.equipes',
    'pedidos.equipes_vendedores',
    'servicos.categoriasfuncoes',
    'servicos.custosmaodeobra',
    'servicos.funcoes',
    'servicos.orcamentos',
    'servicos.receitasdespesas',
    'servicos.tiposfuncoes',
    'servicos.variaveisorcamentarias',
    'estoque.regrasdepagamento',
    'crm.itensprocessarcontaspagar',
    'ns.locaisdeuso',
    'servicos.ordensservicos',
    'servicos.tiposprojetos',
    'estoque.perfiltrib_est',
    'estoque.perfiltrib_fed',
    'ns.df_docfis',
    'estoque.figurastributarias',
    'estoque.operacoes',
    'crm.midiasorigem',
    'crm.negociosoperacoes',
    'crm.promocoesleads',
    'crm.segmentosatuacao',
    'servicos.componentes',
    'servicos.servicostecnicos',
    'servicos.tiposservicos',
    'financas.contas',
]

_entidades_particionadas_por_empresa = [
    'estoque.motoristas',
    'estoque.veiculos',
    #'persona.acordosmp9362020',
    #'persona.beneficios',,#'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.condicoesambientestrabalho',
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.eventos',
    'persona.funcoes',
    'persona.horarios',
    'persona.jornadas',
    'persona.membroscipa',
    'persona.processos',
    'persona.rubricasponto',
    'persona.tiposfuncionarios',
    'ns.configuracoes',
    #'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.trabalhadores',
    'pedidos.clientesvendedores',
    'ns.empresas',
    'pedidos.locaisdeestoquevendedores',
    'ns.estabelecimentos',
    'persona.admissoespreliminares',
    'persona.ambientes',
    'persona.cargos',
    'persona.faltastrabalhadores',
    'persona.movimentos',
    'persona.movimentosponto',
    'pedidos.tabelasdeprecosvendedores',
    'pedidos.produtosvendedores',
    'estoque.regrasdepagamento',
    'estoque.entregadores',
    'estoque.romaneios',
    'estoque.tabelasdeprecos',
    'estoque.perfiltrib_est',
    'estoque.perfiltrib_fed',
    'estoque.figurastributarias',
    'estoque.operacoes',
]

_entidades_particionadas_por_estabelecimento = [
    'ns.configuracoes',
    'persona.movimentosponto',
    'persona.ambientes',
    'persona.cargos',
    'compras.negociacoes',
    'compras.propostascotacoes',
    'compras.requisicoescompras',
    'compras.solicitacoesprodutosservicos',
    'crm.contratostecnicos',
    #'estoque.acordosfornecimentoprodutos', nao faz mais parte da sinc
    #'estoque.custosintermediarios', não faz mais parte sync
    'estoque.figurastributariastemplates',
    'estoque.locaisdeestoques',
    'estoque.locaisdeestoquesenderecos',
    'estoque.locaisdeestoquesoperacoes',
    'estoque.ra',
    'estoque.saldoslocaisdeestoques',
    'financas.contratos',
    'ns.df_enderecos_retiradasentregas',
    'ns.feriados',
    'pedidos.configuracoes_aprovacoes',
    'persona.apontamentos',
    'persona.departamentos',
    'persona.mudancastrabalhadores',
    #'servicos.orcamentositensfaturamento', não faz mais parte sync
    'servicos.atendimentos',
    'ns.estabelecimentosconjuntos',
    'financas.titulos',
    'ns.contaspadroes',
    'ns.numeros_docfis',
    'ns.obras',
    'estoque.tabelasdeprecosestabelecimentos',
]

def medir_tempo(alias=None, out_func=print, color=94):
    def decorator(func):
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            resultado = func(*args, **kwargs)
            fim = time.perf_counter()
            nome = alias if alias else func.__name__
            duracao = fim - inicio
            if duracao < 60:
                _text = f"{nome} executado em {duracao:.3f} segundos"
                if color>0:
                    out_func(f"\033[{color}m{_text}\033[0m")
                else:
                    out_func(_text)
            elif duracao < 3600:
                minutos = duracao // 60
                segundos = duracao % 60
                _text = f"{nome} executado em {minutos:.0f} minutos e {segundos:.3f} segundos"
                if color>0:
                    out_func(f"\033[{color}m{_text}\033[0m")
                else:
                    out_func(_text)
            else:
                horas = duracao // 3600
                minutos = (duracao % 3600) // 60
                segundos = duracao % 60
                _text = f"{nome} executado em {horas:.0f} horas, {minutos:.0f} minutos e {segundos:.3f} segundos"
                if color>0:
                    out_func(f"\033[{color}m{_text}\033[0m")
                else:
                    out_func(_text)
            return resultado
        return wrapper
    return decorator


class Environment(Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    QA = "QA"
    PROD = "PROD"


TAMANHO_PAGINA: int = 100

# Flags trace
_E_SEND_DATA = False
_E_CHECK_INT = False


AUTH_HEADER = 'X-API-Key'

# Lista antes do movimento de lançar o integrador com Urgência
entidades_integracao_old: List[str] = [
    # --- apenas testes ---
    ## "persona.valestransportespersonalizadostrabalhadores"
    # --- Dimensoes ---
    'ns.gruposempresariais',
    'ns.empresas',
    'ns.estabelecimentos',
    'ns.configuracoes',
    'financas.bancos',
    'persona.faixas',
    'ns.obras',
    'persona.lotacoes',
    'ponto.regras',# ns.empresas
    'persona.sindicatos',
    'ns.feriados',
    'persona.instituicoes',
    'persona.eventos',
    'persona.tiposdocumentoscolaboradores',
    'persona.tiposhistoricos',
    'persona.tiposanexos',
    'persona.processos',
    'persona.ambientes',
    'persona.condicoesambientestrabalho',
    'persona.departamentos',
    'persona.funcoes',
    'persona.jornadas',
    'persona.horarios',
    'persona.horariosespeciais',
    'persona.cargos',
    'persona.niveiscargos',
    'persona.tiposfuncionarios',
    'persona.trabalhadores',
    'persona.dependentestrabalhadores',
    'persona.escalasfolgastrabalhadores',
    'persona.beneficios',
    'persona.concessionariasvts',
    'persona.tarifasconcessionariasvtstrabalhadores',
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.historicos',
    'persona.medicos',
    'persona.rubricasponto',
    #'persona.rubricasapontamento',só na web???
    # Fatos
    'persona.compromissostrabalhadores',
    'persona.convocacoestrabalhadores',
    'persona.dispensavalestransportestrabalhadores',
    'persona.emprestimostrabalhadores',
    'persona.historicosadiantamentosavulsos',
    'persona.adiantamentosavulsos',
    'persona.membroscipa',
    'persona.reajustessindicatos',
    'persona.reajustestrabalhadores',
    'ponto.compensacoeslancamentos',
    'ponto.pagamentoslancamentos',
    'persona.admissoespreliminares',# --resolver fk solicitacoesadmissoes
    'persona.avisosferiastrabalhadores', # resolver kf solicitacoesferias
    'persona.pendenciaspagamentos',
    'persona.documentoscolaboradores',
    'persona.faltastrabalhadores', # resolver fk solicitacoesfaltas
    'persona.mudancastrabalhadores',
    'ponto.diascompensacoestrabalhadores',
    'persona.afastamentostrabalhadores',
    'ponto.atrasosentradascompensaveistrabalhadores',
    'ponto.saidasantecipadascompensaveistrabalhadores',
    'persona.beneficiostrabalhadores',
    'persona.movimentosponto',
    'persona.movimentos',
    #'persona.calculostrabalhadores' Não será reativada
]

_entidades_particionadas_por_grupo_old = ['ns.gruposempresariais','ns.empresas', 'ns.configuracoes']

_entidades_particionadas_por_empresa_old = [
    'ns.configuracoes',
    'persona.movimentosponto',
    'ns.estabelecimentos',
    'persona.trabalhadores',
    'persona.processos',
    'persona.jornadas',
    'persona.ambientes',
    'persona.funcoes',
    'persona.cargos',
    #'persona.beneficios',#'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.membroscipa',
    'persona.movimentos',
    'persona.rubricasponto',
    'persona.condicoesambientestrabalho',
    'persona.tiposfuncionarios',
    'persona.horarios',
    'persona.admissoespreliminares',
    'persona.eventos',
    #'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
]

_entidades_particionadas_por_estabelecimento_old = [
    'ns.configuracoes',
    'ns.obras',
    'persona.movimentosponto',
    'persona.trabalhadores',
    'ns.configuracoes',
    'persona.processos',
    'persona.jornadas',
    'persona.ambientes',
    'persona.funcoes',
    'persona.cargos',
    #'persona.beneficios',#'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.membroscipa',
    'persona.movimentos',
    'persona.rubricasponto',
    'persona.condicoesambientestrabalho',
    'persona.tiposfuncionarios',
    'persona.horarios',
    'persona.admissoespreliminares',
    'persona.eventos',
    #'persona.lotacoes' Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
]