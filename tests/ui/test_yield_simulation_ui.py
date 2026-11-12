"""Yield simulation UI tests."""

import pytest
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage
from pages.navbar_component import NavbarComponent


# ==========================================
# 1. CAMADA PAGE OBJECT (Modelada internamente)
# ==========================================
class YieldSimulatorPage(BasePage):
    """Representa a aba do Simulador de Rentabilidade Mês a Mês (YieldSimulator.jsx)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Mapeia o campo de meses (spinbutton ou input numérico)
        self.input_meses = page.locator("input[type='number'], input[type='text'], [role='spinbutton']").first
        # Mapeia o botão exato visto na tela: "Calcular Evolução"
        self.botao_calcular = page.locator("button:has-text('Calcular Evolução')").first

        # Estruturas de saída: Grid de meses e Tabela discriminada por ativo
        # (Ajustados com seletores abrangentes caso os data-testid reais variem na SPA)
        self.grid_meses = page.locator("[data-testid='yield-months-grid'], .grid-meses, table, .results-container").first
        self.cards_meses = page.locator("[data-testid^='month-card-'], .month-card, tbody tr")
        self.tabela_ativos = page.locator("[data-testid='table-yield-by-asset'], table").first
        self.linhas_tabela_ativos = page.locator("[data-testid='table-yield-by-asset'] tbody tr, table tbody tr")

    def definir_meses_projecao(self, meses: int):
        """Preenche o campo de meses e clica no botão 'Calcular Evolução'."""
        self.input_meses.wait_for(state="visible")
        self.input_meses.click()
        self.input_meses.fill("")  # Limpa o campo antes de preencher
        self.input_meses.fill(str(meses))
        
        # Clica no botão de cálculo para renderizar os resultados na SPA
        if self.botao_calcular.is_visible():
            self.botao_calcular.click()


# ==========================================
# 2. FIXTURE AUXILIAR LOCAL
# ==========================================
@pytest.fixture
def yield_page(page: Page) -> YieldSimulatorPage:
    return YieldSimulatorPage(page)


# ==========================================
# 3. CAMADA DE TESTES E2E
# ==========================================
def test_ajuste_projecao_e_renderizacao_grid_meses(
    logged_page: Page,
    navbar: NavbarComponent,
    yield_page: YieldSimulatorPage
):
    """Valida o ajuste do input de meses e a renderização do grid/resultado mensal."""
    navbar.navegar_para_simulador()

    meses_alvo = 12
    yield_page.definir_meses_projecao(meses_alvo)

    # Valida que os resultados aparecem após o clique em Calcular Evolução
    expect(yield_page.grid_meses).to_be_visible(timeout=5000)


def test_projecao_limite_maximo_60_meses(
    logged_page: Page,
    navbar: NavbarComponent,
    yield_page: YieldSimulatorPage
):
    """Valida o comportamento da interface no limite superior de 60 meses."""
    navbar.navegar_para_simulador()

    meses_maximo = 60
    yield_page.definir_meses_projecao(meses_maximo)

    expect(yield_page.grid_meses).to_be_visible(timeout=5000)


def test_renderizacao_tabela_discriminada_por_ativo(
    logged_page: Page,
    navbar: NavbarComponent,
    yield_page: YieldSimulatorPage
):
    """Valida se a tabela discriminada por tipo de ativo é exibida com registros."""
    navbar.navegar_para_simulador()
    yield_page.definir_meses_projecao(24)

    expect(yield_page.tabela_ativos).to_be_visible(timeout=5000)
    assert yield_page.linhas_tabela_ativos.count() > 0, "A tabela discriminada por ativo não apresentou nenhum registro."