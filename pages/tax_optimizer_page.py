"""Tax optimizer page interactions."""
from playwright.sync_api import Page
from pages.base_page import BasePage


class TaxOptimizerPage(BasePage):
    """Encapsula seletores e ações da tela Otimizador Fiscal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.input_valor_resgate = page.locator(
            "[data-testid='input-tax-amount'], input[type='number']"
        ).first
        self.botao_simular = page.locator(
            "[data-testid='btn-simulate-tax'], button:has-text('Simular')"
        ).first
        self.card_melhor_opcao = page.locator(
            "[data-testid='card-best-tax-option'], "
            "tr:has-text('MELHOR OPÇÃO'), "
            "td:has-text('MELHOR OPÇÃO')"
        ).first

    def preencher_valor_resgate(self, valor: str):
        self.input_valor_resgate.wait_for(state="visible", timeout=10000)
        self.input_valor_resgate.fill(valor)

    def submeter_analise(self):
        self.botao_simular.click()

    def realizar_simulacao(self, valor: str):
        self.preencher_valor_resgate(valor)
        self.submeter_analise()
