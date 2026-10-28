"""Asset manager UI tests."""
import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.asset_manager_page import AssetManagerPage


# ---------------------------------------------------------------------------
# Integrante 2 — Gerenciar Taxas (AssetManager.jsx — US05)
# ---------------------------------------------------------------------------

# A taxa é GLOBAL (vale para todos os grupos), então alteramos um ativo de
# teste e sempre devolvemos a taxa original ao final de cada teste.
ATIVO_TESTE = "ATIVO_TESTE_UPSERT_QA"


@pytest.fixture
def asset_manager_page(page: Page) -> AssetManagerPage:
    return AssetManagerPage(page)


@pytest.fixture
def tela_taxas(logged_page: Page, navbar: NavbarComponent, asset_manager_page: AssetManagerPage):
    """Abre a aba Gerenciar Taxas já autenticado."""
    navbar.navegar_para_gerenciar_taxas()
    asset_manager_page.aguardar_tabela_carregada()
    return asset_manager_page


@pytest.fixture
def taxa_original(tela_taxas: AssetManagerPage):
    """Guarda a taxa do ativo de teste e a restaura depois do teste."""
    original = tela_taxas.obter_taxa_salva(ATIVO_TESTE)
    yield original
    tela_taxas.alterar_taxa(ATIVO_TESTE, original)
    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text(f"{original}% a.a.")


def test_tabela_publica_de_taxas_e_exibida(tela_taxas: AssetManagerPage):
    """A tabela lista os ativos com as colunas esperadas."""
    expect(tela_taxas.tabela_taxas).to_be_visible()
    expect(tela_taxas.cabecalhos_tabela).to_have_text([
        "Ativo", "Categoria", "Taxa Anual Salva (% a.a.)", "Nova Taxa (% a.a.)", "Ação"
    ])
    assert {"Poupança", "CDB", "Bitcoin"} <= set(tela_taxas.obter_nomes_ativos())


def test_tabela_nao_repete_ativos(tela_taxas: AssetManagerPage):
    """Cada ativo aparece uma única vez na tabela."""
    nomes = [nome.lower() for nome in tela_taxas.obter_nomes_ativos()]
    assert len(nomes) == len(set(nomes))


def test_campo_nova_taxa_vem_preenchido_com_taxa_salva(tela_taxas: AssetManagerPage):
    """O input de nova taxa já vem com o valor atualmente salvo."""
    taxa_salva = tela_taxas.obter_taxa_salva("CDB")
    expect(tela_taxas.campo_nova_taxa("CDB")).to_have_value(taxa_salva)


def test_alterar_taxa_exibe_sucesso_e_atualiza_taxa_salva(tela_taxas: AssetManagerPage, taxa_original):
    """Salvar uma nova taxa mostra a mensagem de sucesso e atualiza a coluna salva."""
    nova_taxa = "7.77" if taxa_original != "7.77" else "8.88"

    tela_taxas.alterar_taxa(ATIVO_TESTE, nova_taxa)

    expect(tela_taxas.mensagem_sucesso).to_be_visible(timeout=10000)
    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text(f"{nova_taxa}% a.a.")


def test_taxa_alterada_persiste_apos_recarregar(
    tela_taxas: AssetManagerPage, taxa_original, navbar: NavbarComponent
):
    """Depois de salvar, a nova taxa continua lá ao recarregar a página."""
    nova_taxa = "6.66" if taxa_original != "6.66" else "5.55"

    tela_taxas.alterar_taxa(ATIVO_TESTE, nova_taxa)
    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text(f"{nova_taxa}% a.a.", timeout=10000)

    tela_taxas.recarregar()
    navbar.navegar_para_gerenciar_taxas()
    tela_taxas.aguardar_tabela_carregada()

    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text(f"{nova_taxa}% a.a.")


def test_taxa_com_virgula_e_aceita(tela_taxas: AssetManagerPage, taxa_original):
    """A taxa digitada com vírgula decimal (padrão brasileiro) é convertida e salva."""
    tela_taxas.alterar_taxa(ATIVO_TESTE, "4,25")

    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text("4.25% a.a.", timeout=10000)


def test_taxa_nao_numerica_exibe_erro(tela_taxas: AssetManagerPage):
    """Texto não numérico não é enviado e mostra mensagem de erro."""
    taxa_antes = tela_taxas.obter_taxa_salva(ATIVO_TESTE)

    tela_taxas.alterar_taxa(ATIVO_TESTE, "abc")

    expect(tela_taxas.mensagem_erro).to_have_text("Por favor, digite um valor numérico válido.")
    expect(tela_taxas.celula_taxa_salva(ATIVO_TESTE)).to_have_text(f"{taxa_antes}% a.a.")
