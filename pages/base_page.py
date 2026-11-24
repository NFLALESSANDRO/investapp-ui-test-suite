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

    def listar_imagens_sem_alt(self) -> list:
        """Retorna lista de imagens visíveis que não possuem atributo alt preenchido."""
        return self.page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs
                .filter(img => img.offsetParent !== null)
                .filter(img => !img.hasAttribute('alt') || img.getAttribute('alt').trim() === '')
                .map(img => img.src || 'img-sem-src');
        }""")

    def verificar_contraste_basico_elementos(self) -> bool:
        """Verifica se o texto principal e o fundo da página possuem cores distintas."""
        return self.page.evaluate("""() => {
            const bodyStyle = window.getComputedStyle(document.body);
            return bodyStyle.color !== bodyStyle.backgroundColor;
        }""")

    def obter_botoes_sem_texto_ou_aria_label(self) -> list:
        """Verifica se botões visíveis possuem texto ou aria-label para leitores de tela."""
        return self.page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons
                .filter(btn => btn.offsetParent !== null)
                .filter(btn => {
                    const text = (btn.innerText || '').trim();
                    const aria = (btn.getAttribute('aria-label') || '').trim();
                    const title = (btn.getAttribute('title') || '').trim();
                    return !text && !aria && !title;
                })
                .map(btn => btn.outerHTML.slice(0, 80));
        }""")

    def listar_inputs_desabilitados(self) -> int:
        """Retorna a quantidade de inputs/botões atualmente desabilitados na tela."""
        return self.page.locator("input:disabled, button:disabled, select:disabled").count()
