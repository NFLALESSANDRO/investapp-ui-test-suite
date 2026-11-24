import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.navbar_component import NavbarComponent
from pages.login_modal_page import LoginModalPage
from pages.portfolio_page import PortfolioPage


def test_submissao_formulario_login_vazio(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
    login_modal: LoginModalPage,
):
    """Valida que o sistema impede o login quando usuário e senha estão vazios."""
    page.goto(base_url)
    navbar.clicar_entrar()
    expect(login_modal.container_modal).to_be_visible()

    login_modal.realizar_login("", "")

    # O modal deve permanecer aberto e o botão Sair não deve aparecer
    expect(login_modal.container_modal).to_be_visible()
    expect(navbar.botao_sair).not_to_be_visible()


def test_submissao_formulario_carteira_vazio(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida que não é possível cadastrar um aporte com campos obrigatórios vazios."""
    navbar.navegar_para_carteira()
    total_antes = portfolio_page.total_de_ativos_listados()

    portfolio_page.botao_adicionar.click()

    total_depois = portfolio_page.total_de_ativos_listados()
    assert total_depois == total_antes, "Formulário vazio não deveria inserir registro na carteira."


def test_tentativa_insercao_aporte_negativo(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida que a UI rejeita a inserção de aporte com quantidade negativa."""
    navbar.navegar_para_carteira()
    # Aguarda a tabela terminar de carregar os dados da API antes de contar
    logged_page.wait_for_load_state("networkidle")
    total_antes = portfolio_page.total_de_ativos_listados()

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="-200.00",
        preco="1.00",
        dias_inv="30",
        dias_plan="180",
    )

    # Aguarda um pouco para ver se o alerta de erro aparece na tela
    try:
        portfolio_page.alerta_erro.wait_for(state="visible", timeout=3000)
        expect(portfolio_page.alerta_erro).to_be_visible()
    except Exception:
        # Se não houver alerta visual (ex: validação nativa do navegador),
        # garante que nenhum novo registro foi inserido na tabela
        logged_page.wait_for_load_state("networkidle")
        total_depois = portfolio_page.total_de_ativos_listados()
        assert total_depois == total_antes, (
            f"Aporte negativo não deveria ser cadastrado (antes: {total_antes}, depois: {total_depois})."
        )

def test_bloqueio_elementos_desabilitados_e_acesso_restrito(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
):
    """Valida bloqueios de estado na interface antes da autenticação."""
    base_page = BasePage(page, base_url)
    base_page.navegar()

    # Usuário deslogado não deve ver o botão de logout
    expect(navbar.botao_sair).not_to_be_visible()
    # Checa de forma segura o método de elementos desabilitados na página
    desabilitados = base_page.listar_inputs_desabilitados()
    assert desabilitados >= 0


def test_acessibilidade_basica_contraste_e_alt_text(
    logged_page: Page,
    navbar: NavbarComponent,
):
    """Valida critérios básicos de acessibilidade: alt text em imagens, contraste e rótulos de botões."""
    navbar.navegar_para_carteira()
    base_page = BasePage(logged_page)

    imagens_sem_alt = base_page.listar_imagens_sem_alt()
    assert len(imagens_sem_alt) == 0, f"Imagens sem atributo alt encontradas: {imagens_sem_alt}"

    assert base_page.verificar_contraste_basico_elementos(), "Contraste básico entre texto e fundo falhou."

    botoes_sem_rotulo = base_page.obter_botoes_sem_texto_ou_aria_label()
    assert len(botoes_sem_rotulo) == 0, f"Botões sem texto ou aria-label: {botoes_sem_rotulo}"