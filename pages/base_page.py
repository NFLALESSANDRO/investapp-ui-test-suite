from playwright.sync_api import Page, Locator, expect


class BasePage:
    """Classe base contendo a instância de Page e utilitários de navegação e espera."""

    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

    def navegar(self, path: str = ""):
        """Abre uma URL relativa à base ou a raiz se não informado."""
        url_destino = f"{self.base_url}/{path}".rstrip("/")
        self.page.goto(url_destino if url_destino else self.base_url)

    def obter_titulo(self) -> str:
        """Retorna o título da aba atual."""
        return self.page.title()

    def recarregar(self):
        """Atualiza a página."""
        self.page.reload()
