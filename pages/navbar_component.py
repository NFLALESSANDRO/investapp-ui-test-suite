from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class NavbarComponent(BasePage):
    """Encapsula as ações e seletores da barra de navegação global."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.botao_entrar = page.locator("[data-testid='btn-open-login']")
        self.botao_sair = page.locator("[data-testid='btn-logout']")
        self.link_carteira = page.locator("[data-testid='nav-portfolio']")
        self.link_simulador_rendimento = page.locator("[data-testid='nav-yield-sim']")
        self.link_otimizador_fiscal = page.locator("[data-testid='nav-tax-sim']")
        self.link_gerenciar_taxas = page.locator("[data-testid='nav-asset-rates']")

    def clicar_entrar(self):
        self.botao_entrar.click()

    def clicar_sair(self):
        self.botao_sair.click()

    def navegar_para_carteira(self):
        self.link_carteira.click()

    def navegar_para_simulador(self):
        self.link_simulador_rendimento.click()

    def navegar_para_otimizador_fiscal(self):
        self.link_otimizador_fiscal.click()

    def navegar_para_gerenciar_taxas(self):
        self.link_gerenciar_taxas.click()
