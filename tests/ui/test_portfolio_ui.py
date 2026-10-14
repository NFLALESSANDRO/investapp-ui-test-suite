import itertools
import random

import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


# ---------------------------------------------------------------------------
# Integrante 3 — Cadastro de novos aportes na carteira (Portfolio.jsx — US02)
# ---------------------------------------------------------------------------

# Prazo planejado único por execução: a conta de homologação é compartilhada
# pelo grupo, então cada teste localiza (e limpa) somente as linhas que criou.
_prazos_unicos = itertools.count(random.randint(1000, 8000) * 10)


def gerar_prazo_planejado_unico() -> str:
    return str(next(_prazos_unicos))


@pytest.fixture
def carteira(logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage):
    """Abre a aba Carteira já autenticado e remove, ao final, os aportes criados no teste."""
    navbar.navegar_para_carteira()
    portfolio_page.aguardar_carteira_carregada()

    linhas_criadas = []
    yield portfolio_page, linhas_criadas

    for linha in linhas_criadas:
        if linha.count() > 0:
            portfolio_page.excluir_linha(linha)


def test_cadastrar_novo_aporte_carteira(carteira):
    """Valida a criação de aporte e renderização exata na tabela da carteira."""
    portfolio_page, linhas_criadas = carteira
    dias_inv = "0"
    dias_plan = gerar_prazo_planejado_unico()

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="2500.00",
        preco="1.00",
        dias_inv=dias_inv,
        dias_plan=dias_plan
    )

    # Busca a linha específica recém-criada combinando Ativo + Prazo em dias
    linha_aporte = portfolio_page.obter_linha_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    linhas_criadas.append(linha_aporte)

    expect(linha_aporte).to_be_visible(timeout=5000)
    expect(linha_aporte).to_contain_text("Poupança")
    expect(linha_aporte).to_contain_text(f"{dias_inv} / {dias_plan} dias")
    expect(portfolio_page.alerta_erro).not_to_be_visible()


def test_select_lista_ativos_com_taxa_anual(carteira):
    """O select de ativos é carregado da API e cada opção exibe sua taxa anual."""
    portfolio_page, _ = carteira

    rotulos = portfolio_page.obter_rotulos_ativos_disponiveis()

    assert len(rotulos) > 0
    assert all(rotulo.endswith("% a.a.)") for rotulo in rotulos)
    nomes = [rotulo.rsplit(" (", 1)[0] for rotulo in rotulos]
    assert {"Poupança", "CDB", "Bitcoin"} <= set(nomes)
    assert len(nomes) == len(set(nomes)), "O select não deve repetir ativos com o mesmo nome"


def test_formulario_inicia_com_valores_padrao(carteira):
    """Ao abrir a carteira, o formulário vem com o 1º ativo, 30/365 dias e valores em branco."""
    portfolio_page, _ = carteira

    primeiro_ativo = portfolio_page.obter_rotulos_ativos_disponiveis()[0].rsplit(" (", 1)[0]
    valores = portfolio_page.obter_valores_formulario()

    assert valores == {
        "ativo": primeiro_ativo,
        "quantidade": "",
        "preco": "",
        "dias_inv": "30",
        "dias_plan": "365",
    }


@pytest.mark.parametrize("ativo", ["Poupança", "CDB", "LCI", "Tesouro Direto", "Bitcoin"])
def test_cadastro_de_cada_tipo_de_ativo_exibe_taxa_correta(carteira, ativo):
    """Cada ativo cadastrado aparece na tabela com a mesma taxa anunciada no select."""
    portfolio_page, linhas_criadas = carteira
    dias_plan = gerar_prazo_planejado_unico()
    taxa_esperada = portfolio_page.obter_taxa_do_ativo_no_select(ativo)

    portfolio_page.cadastrar_aporte(ativo, "3", "150.00", "10", dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo(ativo, "10", dias_plan)
    linhas_criadas.append(linha)
    expect(linha).to_be_visible(timeout=5000)
    expect(portfolio_page.celula_taxa(linha)).to_have_text(taxa_esperada)


def test_valor_atual_igual_quantidade_vezes_preco_sem_dias_decorridos(carteira):
    """Com 0 dias decorridos não há rendimento: Valor Atual = quantidade × preço pago."""
    portfolio_page, linhas_criadas = carteira
    dias_plan = gerar_prazo_planejado_unico()

    portfolio_page.cadastrar_aporte("CDB", "10", "100.00", "0", dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo("CDB", "0", dias_plan)
    linhas_criadas.append(linha)
    expect(linha).to_be_visible(timeout=5000)
    expect(linha).to_contain_text("R$ 1.000,00")


def test_formulario_limpa_quantidade_e_preco_apos_cadastro(carteira):
    """Após o sucesso, quantidade e preço são limpos; ativo e prazos permanecem preenchidos."""
    portfolio_page, linhas_criadas = carteira
    dias_plan = gerar_prazo_planejado_unico()

    portfolio_page.cadastrar_aporte("LCA", "5", "200.00", "45", dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo("LCA", "45", dias_plan)
    linhas_criadas.append(linha)
    expect(linha).to_be_visible(timeout=5000)
    expect(portfolio_page.input_quantidade).to_have_value("")
    expect(portfolio_page.input_preco_compra).to_have_value("")
    assert portfolio_page.obter_valores_formulario()["ativo"] == "LCA"
    expect(portfolio_page.input_dias_investidos).to_have_value("45")
    expect(portfolio_page.input_dias_planejados).to_have_value(dias_plan)


def test_cadastro_incrementa_quantidade_de_linhas(carteira):
    """Cada novo aporte acrescenta exatamente uma linha à tabela da carteira."""
    portfolio_page, linhas_criadas = carteira
    total_inicial = portfolio_page.total_de_ativos_listados()
    dias_plan = gerar_prazo_planejado_unico()

    portfolio_page.cadastrar_aporte("Fundo DI", "1", "1000.00", "0", dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo("Fundo DI", "0", dias_plan)
    linhas_criadas.append(linha)
    expect(linha).to_be_visible(timeout=5000)
    expect(portfolio_page.linhas_tabela_carteira).to_have_count(total_inicial + 1)


# ---------------------------------------------------------------------------
# Integrante 4 — Exclusão de ativos e métricas consolidadas
# ---------------------------------------------------------------------------

def test_remover_ativo_recalcula_patrimonio(logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage):
    """Valida a exclusão do primeiro ativo e conferência da redução na tabela."""
    navbar.navegar_para_carteira()

    total_inicial = portfolio_page.total_de_ativos_listados()

    if total_inicial > 0:
        portfolio_page.excluir_primeiro_ativo()
        # Aguarda a tabela re-renderizar para o novo total esperado
        expect(portfolio_page.linhas_tabela_carteira).to_have_count(total_inicial - 1, timeout=5000)
