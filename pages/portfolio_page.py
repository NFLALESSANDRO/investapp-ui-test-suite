from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class PortfolioPage(BasePage):
    """Representa a aba da Carteira de Investimentos (Portfolio.jsx)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Formulário de Cadastro
        self.select_ativo = page.locator("[data-testid='select-asset-name']")
        self.input_quantidade = page.locator("[data-testid='input-asset-amount']")
        self.input_preco_compra = page.locator("[data-testid='input-asset-price']")
        self.input_dias_investidos = page.locator("[data-testid='input-asset-days-invested']")
        self.input_dias_planejados = page.locator("[data-testid='input-asset-planned-days']")
        self.botao_adicionar = page.locator("[data-testid='btn-add-asset']")

        # Indicadores e Tabela
        self.card_patrimonio_total = page.locator("[data-testid='summary-current-val']")
        self.linhas_tabela_carteira = page.locator("[data-testid='table-portfolio'] tbody tr")
        self.alerta_erro = page.locator("[data-testid='portfolio-error']")

        # Seção da carteira (renderizada apenas para usuário autenticado)
        self.secao_carteira = page.locator("[data-testid='section-portfolio']")
        self.opcoes_ativo = self.select_ativo.locator("option")

    def cadastrar_aporte(self, ativo: str, quantidade: str, preco: str, dias_inv: str, dias_plan: str):
        """Preenche todos os campos do formulário e submete o novo aporte."""
        self.select_ativo.wait_for(state="visible")
        try:
            self.select_ativo.select_option(value=ativo)
        except Exception:
            self.select_ativo.select_option(label=f"{ativo}")
        self.input_quantidade.fill(quantidade)
        self.input_preco_compra.fill(preco)
        self.input_dias_investidos.fill(dias_inv)
        self.input_dias_planejados.fill(dias_plan)
        self.botao_adicionar.click()

    def obter_linha_por_ativo_e_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """
        Localiza especificamente a linha do ativo que corresponde aos dias cadastrados,
        evitando colisão com outros aportes do mesmo ativo.
        """
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).filter(has_text=texto_prazo).first

    def obter_rotulos_ativos_disponiveis(self) -> list[str]:
        """Retorna o texto de cada opção do select de ativos (ex: 'CDB (10.5% a.a.)')."""
        self.select_ativo.wait_for(state="visible")
        self.opcoes_ativo.first.wait_for(state="attached")
        return [rotulo.strip() for rotulo in self.opcoes_ativo.all_inner_texts()]

    def obter_taxa_do_ativo_no_select(self, nome_ativo: str) -> str:
        """Extrai a taxa exibida na opção do select (ex: 'CDB (10.50% a.a.)' -> '10.50%')."""
        for rotulo in self.obter_rotulos_ativos_disponiveis():
            if rotulo.startswith(f"{nome_ativo} ("):
                return rotulo[len(nome_ativo) + 2:].replace(" a.a.)", "")
        raise ValueError(f"Ativo '{nome_ativo}' não encontrado no select.")

    def obter_valores_formulario(self) -> dict:
        """Retorna os valores atuais de cada campo do formulário de aporte."""
        return {
            "ativo": self.select_ativo.input_value(),
            "quantidade": self.input_quantidade.input_value(),
            "preco": self.input_preco_compra.input_value(),
            "dias_inv": self.input_dias_investidos.input_value(),
            "dias_plan": self.input_dias_planejados.input_value(),
        }

    def celula_taxa(self, linha: Locator) -> Locator:
        """Badge com a taxa anual (% a.a.) exibida na linha informada."""
        return linha.locator(".badge-rate")

    def obter_texto_patrimonio_total(self) -> str:
        """Texto do card PATRIMÔNIO ATUAL (ex: 'R$ 1.234,56')."""
        return self.card_patrimonio_total.inner_text()

    def aguardar_carteira_carregada(self):
        """Aguarda a tabela da carteira sair do estado inicial vazio ou estabilizar."""
        self.secao_carteira.wait_for(state="visible")
        self.page.wait_for_load_state("networkidle")

    def excluir_linha(self, linha: Locator):
        """Exclui o aporte da linha informada (usado na limpeza dos dados de teste)."""
        linha.locator("[data-testid^='btn-delete-asset-']").click()
        linha.wait_for(state="detached")

    def obter_ultimo_ativo_cadastrado(self, nome_ativo: str) -> Locator:
        """Retorna a última linha inserida na tabela para o ativo informado."""
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).last

    def excluir_primeiro_ativo(self):
        """Clica no botão de exclusão da primeira linha da tabela."""
        botao_excluir = self.linhas_tabela_carteira.first.locator("[data-testid^='btn-delete-asset-']")
        botao_excluir.click()

    def total_de_ativos_listados(self) -> int:
        """Retorna o número atual de registros na tabela da carteira ignorando a mensagem de vazio."""
        self.page.wait_for_selector("[data-testid='table-portfolio'] tbody", timeout=5000)
        # Se contiver a mensagem de tabela vazia (colSpan="7"), o total é 0
        if self.linhas_tabela_carteira.filter(has_text="Nenhum ativo cadastrado").count() > 0:
            return 0
        return self.linhas_tabela_carteira.count()
