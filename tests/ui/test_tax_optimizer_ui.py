from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.tax_optimizer_page import TaxOptimizerPage


def test_otimizador_fiscal_menor_ir(
    logged_page: Page,
    navbar: NavbarComponent,
    tax_optimizer_page: TaxOptimizerPage
):
    """Valida a indicação de melhor opção de resgate com menor IR."""
    navbar.navegar_para_otimizador_fiscal()
    tax_optimizer_page.realizar_simulacao("1000.00")

    expect(
        tax_optimizer_page.card_melhor_opcao
    ).to_be_visible(timeout=5000)
    expect(
        tax_optimizer_page.card_melhor_opcao
    ).to_contain_text("MELHOR OPÇÃO")
