"""Asset manager page interactions."""
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class AssetManagerPage(BasePage):
    """Representa a aba Gerenciar Taxas (AssetManager.jsx — US05)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.secao = page.locator("[data-testid='section-asset-manager']")
        self.tabela_taxas = page.locator("[data-testid='table-asset-rates']")
        self.cabecalhos_tabela = self.tabela_taxas.locator("thead th")
        self.linhas_tabela = self.tabela_taxas.locator("tbody tr")
        self.mensagem_sucesso = self.secao.locator(":scope > div").filter(has_text="salva com sucesso")
        self.mensagem_erro = self.secao.locator(".error-message")

    def aguardar_tabela_carregada(self):
        """Aguarda a tabela de taxas ser preenchida pela API."""
        self.secao.wait_for(state="visible")
        self.linhas_tabela.first.wait_for(state="visible")

    def obter_nomes_ativos(self) -> list[str]:
        """Retorna o nome de cada ativo listado na tabela (1ª coluna)."""
        return [nome.strip() for nome in self.linhas_tabela.locator("td:first-child").all_inner_texts()]

    def obter_linha_do_ativo(self, nome_ativo: str) -> Locator:
        """Linha da tabela cujo nome do ativo é exatamente o informado."""
        nome_exato = self.page.locator("td:first-child").get_by_text(nome_ativo, exact=True)
        return self.linhas_tabela.filter(has=nome_exato).first

    def celula_taxa_salva(self, nome_ativo: str) -> Locator:
        """Coluna 'Taxa Anual Salva (% a.a.)' do ativo (ex: '10.50% a.a.')."""
        return self.obter_linha_do_ativo(nome_ativo).locator("td").nth(2)

    def campo_nova_taxa(self, nome_ativo: str) -> Locator:
        """Input 'Nova Taxa (% a.a.)' do ativo."""
        return self.obter_linha_do_ativo(nome_ativo).locator("input")

    def obter_taxa_salva(self, nome_ativo: str) -> str:
        """Retorna a taxa salva sem o sufixo (ex: '10.50')."""
        return self.celula_taxa_salva(nome_ativo).inner_text().replace("% a.a.", "").strip()

    def alterar_taxa(self, nome_ativo: str, nova_taxa: str):
        """Digita a nova taxa no input do ativo e clica em 'Salvar Alteração'."""
        self.campo_nova_taxa(nome_ativo).fill(nova_taxa)
        self.obter_linha_do_ativo(nome_ativo).locator("button").click()
