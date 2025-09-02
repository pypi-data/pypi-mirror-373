from typing import List

from enum import Enum

from collections import defaultdict

import time
from datetime import datetime

from nsj_rest_lib.descriptor.filter_operator import FilterOperator

# Pontos de corte de carga inicial para cada entidade
# Alguns poderão ser fixos, outros poderão ser dinâmicos (calculados)
# a idéia é que registre um json com os filtros de campos qque serão passados no restlib
# Esses dados também são usados para efeito de carga contínua e verificação de integridade
_entidades_filtros_integracao: defaultdict = defaultdict(list) | {
    'ns.df_docfis': [
        {
            'campo': 'id_ano',
            'valor': datetime.now().year-1,
            'operador': FilterOperator.GREATER_OR_EQUAL_THAN.value,
            'alias': "id_ano >= Ano atual - 1, /*Pedido*/ tipo = 20, modelo = 'NE', /*Nota Fiscal*/ tipo = (0, 21), modelo = 'NE'"
        },
    ],
    'ns.df_pagamentos':[
        {
            'campo': 'datafatura',
            'valor': f'{datetime.now().year-1}-01-01',
            'operador': FilterOperator.GREATER_OR_EQUAL_THAN.value,
            'alias': "datafatura >= Ano atual - 1"
        }
    ],
    'ns.df_parcelas':[
        {
            'campo': 'competencia',
            'valor': f'{datetime.now().year-1}-01-01',
            'operador': FilterOperator.GREATER_OR_EQUAL_THAN.value,
            'alias': "competencia >= Ano atual - 1"
        }
    ],
    'financas.titulos': [
        {
            'campo': 'emissao',
            'valor': f'{datetime.now().year-1}-01-01',
            'operador': FilterOperator.GREATER_OR_EQUAL_THAN.value,
            'alias': "emissao >= Ano atual - 1"
        },
    ],
    'servicos.ordensdeservicos': [
        {
            'campo': 'data_criacao',
            'valor': f'{datetime.now().year-1}-01-01',
            'operador': FilterOperator.GREATER_OR_EQUAL_THAN.value,
            'alias': "data_criacao >= Ano atual - 1"
        },
    ]
}

class TipoVerificacaoIntegridade(Enum):
    CONTAGEM = "CONTAGEM"      # Compara número de registros entre web e desktop
    IDENTIFICADOR = "ID"       # Compara chaves, identifica registros a criar/excluir
    HASH = "HASH"             # Compara chave + hash, identifica criar/atualizar/excluir
    ATRIBUTO = "ATRIBUTO"     # Como HASH mas detalha campos com diferença

    @classmethod
    def from_str(cls, value: str):
        # Tenta pelo nome
        try:
            return cls[value]
        except KeyError:
            pass

        # Tenta pelo valor
        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"{value!r} não é um nome ou valor válido para {cls.__name__}")

def _filtro_nome(filtro):
    return f"{filtro['campo']}_{filtro['operador']}"


def _cfg_filtros_to_dto_filtro(cfg_filtros: list) -> dict:
    _filtros = {}
    for _filtro in cfg_filtros:
        # Garante que o operador é o correto
        _op = getattr(FilterOperator, _filtro['operador'].upper(), FilterOperator.EQUALS)
        _filtro['operador'] = _op.value
        _filtros[_filtro_nome(_filtro)] = _filtro['valor']

    return _filtros


_ignorar_integridade = [
    'ns.conjuntosfichas',
    'ns.conjuntosservicos',
    'ns.conjuntosfornecedores',
    'ns.conjuntosunidades',
    'ns.conjuntosvendedores',
    'ns.conjuntos',
    'ns.conjuntosclientes',
    'ns.conjuntosprodutos',
    'ns.configuracoes'
]

_entidades_blob = {
    'persona.trabalhadores': ['foto','fotooriginal'],
    'persona.documentoscolaboradores': ['bindocumento']
}

_entidades_integracao: List[str] = [
    'ns.gruposempresariais',
    'ns.empresas',
    'ns.estabelecimentos',
    'ns.tipi',
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
    'persona.condicoesambientestrabalho',
    'pedidos.equipes',
    'pedidos.pessoas_produtos_consumidos',
    'pedidos.equipes_vendedores',
    'ns.pessoasparcelamentos',
    'pedidos.produtos_faixas_precos_vigencias',
    'pedidos.produtos_faixas_precos',
    'pedidos.produtos_faixas_precos_segmentos',
    'persona.membroscipa',
    'estoque.classificacoesfragilidade',
    #'persona.beneficiostrabalhadoressuspensoesadesoes', Não existe local
    #'persona.beneficiostrabalhadoresadesoes', Não existe local
    'ns.conjuntosfichas',
    'persona.ambientes',
    #'ns.configuracaoacessoapi', nao sincronizara
    'ns.pessoasformaspagamentos',
    #'ns.rateios', nao sincronizara
    #'servicos.ordensservicosvisitas', nao sincronizara
    #'persona.gestorestrabalhadores', persona.trabalhadores
    #'persona.itensfaixas', entidade filha
    #'persona.outrosrecebimentostrabalhadores', persona.trabalhadores
    #'persona.processosrubricas', contido em processos
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
    #'persona.processossuspensoes', ja esta em processosrubricas
    'ponto.atrasosentradascompensaveistrabalhadores',
    #'estoque.custosintermediarios', não faz mais parte da sinc
    'ns.conjuntosservicos',
    #'ns.tipi', nao sincronizara
    #'ns.tiposfollowups', nao sincronizara
    #'ns.valoresclassificadoreslista', não sincroniza mais
    #'ponto.pendenciascalculostrabalhadores', persona.trabalhadores
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
    #'financas.contratos', removido após constatar desuso
    #'financas.itenscontratos', removido após constatar desuso
    #'ns.df_servicos', removido pois não é mais usado
    # 'ns.numeros_docfis', nao sincronizara
    #'ns.obras', nao sincronizara
    #'ns.perfisusuario', nao sincronizara
    'ponto.saidasantecipadascompensaveistrabalhadores',
    'ns.estabelecimentosconjuntos',
    #'ns.gruposdeusuariosacessos', nao sincronizara
    'ns.telefones',
    #'servicos.servicoscatalogo', NAO MAIS
    'persona.tiposhistoricos',
    'ns.conjuntosunidades',
    'ns.conjuntosvendedores',
    'financas.contas',
    'financas.layoutscobrancas',
    #'crm.assuntos', não sincroniza mais'
    #'financas.configuracoesbancarias', nao sincroizara
    #'financas.contratosclientespartilhas', Descontinuada em 08/05/2025 junto a contratos
    #'financas.tiposcontas', nao sincronizara
    #'ns.anexosmodulos', removida em 08/05/2025
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
    #'ns.df_linhas',
    'ns.formaspagamentos',
    #'ns.usuarios', nao sincronizara
    #'ns.documentositens', nao sincornizara
    'servicos.servicos',
    'financas.centroscustos',
    #'servicos.ordensservicos', nao sincronizara
    #'financas.classificacoesfinanceiras', nao sincronizara
    #'financas.rateiosfinanceiros', nao sincronizara
    #'persona.avisospreviostrabalhadores', persona.trabalhadores
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
    #'persona.horariosalternativostrabalhadores', persona.trabalhadores
    #'persona.outrosrendimentostrabalhadores', persona.trabalhadores
    'persona.afastamentostrabalhadores',
    'ns.feriados',
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
    #'persona.apontamentos',
    #'servicos.componentes',
    'estoque.perfiltrib_est_validades_impostos',
    #'persona.acordosmp9362020trabalhadores',
    'persona.movimentos',
    'financas.projetos',
    #'servicos.orcamentoscustosmateriais',
    #'estoque.produtosnumerosdeserie',
    #'estoque.acordosfornecimentoprodutositens' não faz mais parte da sinc
]

_entidades_particionadas_por_grupo = [
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
    #'ns.df_enderecos_retiradasentregas', nao particiona, ignorar planilha
    #'ns.feriados', particionamento flexível
    'pedidos.configuracoes_aprovacoes',
    'persona.apontamentos',
    'persona.departamentos',
    #'persona.mudancastrabalhadores', remoção do particionamento, por conta bug na Nasajon
    #'servicos.orcamentositensfaturamento', não faz mais parte sync
    'servicos.atendimentos',
    'ns.estabelecimentosconjuntos',
    'financas.titulos',
    'ns.contaspadroes',
    'ns.numeros_docfis',
    'ns.obras',
    'estoque.tabelasdeprecosestabelecimentos',
]

def medir_tempo(alias=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            resultado = func(*args, **kwargs)
            fim = time.perf_counter()
            nome = alias if alias else func.__name__
            duracao = fim - inicio
            if duracao < 60:
                _text = f"{nome} executado(a) em {duracao:.3f} segundos"
            elif duracao < 3600:
                minutos = duracao // 60
                segundos = duracao % 60
                _text = f"{nome} executado(a) em {minutos:.0f} minutos e {segundos:.3f} segundos"
            else:
                horas = duracao // 3600
                minutos = (duracao % 3600) // 60
                segundos = duracao % 60
                _text = f"{nome} executado(a) em {horas:.0f} horas, {minutos:.0f} minutos e {segundos:.3f} segundos"
            return resultado, _text
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


if __name__ == '__main__':
    print(len(_entidades_integracao))