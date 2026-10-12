from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def test_cadastrar_novo_aporte_carteira(logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage):
    """Valida a criação de aporte e renderização exata na tabela da carteira."""
    navbar.navegar_para_carteira()

    dias_inv = "0"
    dias_plan = "365"

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="2500.00",
        preco="1.00",
        dias_inv=dias_inv,
        dias_plan=dias_plan
    )

    # Busca a linha específica recém-criada combinando Ativo + Prazo em dias
    linha_aporte = portfolio_page.obter_linha_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    
    expect(linha_aporte).to_be_visible(timeout=5000)
    expect(linha_aporte).to_contain_text("Poupança")


def test_remover_ativo_recalcula_patrimonio(logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage):
    """Valida a exclusão do primeiro ativo e conferência da redução na tabela."""
    navbar.navegar_para_carteira()

    total_inicial = portfolio_page.total_de_ativos_listados()

    if total_inicial > 0:
        portfolio_page.excluir_primeiro_ativo()
        # Aguarda a tabela re-renderizar para o novo total esperado
        expect(portfolio_page.linhas_tabela_carteira).to_have_count(total_inicial - 1, timeout=5000)
